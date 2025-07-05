from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import ChatHistory,ChatSession
from django.contrib.auth.decorators import login_required
import trafilatura
import re
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
# from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
import os
import pickle
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import logging
import requests
import logging

logger = logging.getLogger(__name__)



# Initialize Groq LLM
GROQ_API_KEY = "Enter Your API KEY"
llm = ChatGroq(
    temperature=0,
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.3-70b-versatile"
)
# File paths
preloaded_faiss_path = "main/faiss_store_groq.pkl"  # Preloaded FAISS store

# Initialize vectorstore as None at the beginning
vectorstore = None

def home(request):
    return render(request, 'home.html')

@csrf_exempt
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

@csrf_exempt
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

from django.http import JsonResponse

@login_required
def process_urls(request):
    preloaded_faiss_path = "faiss_index.pkl"  # Save FAISS index here

    if request.method == 'POST':
        urls = request.POST.getlist('urls')
        query = request.POST.get('query')

        # Processing URLs (if provided)
        if urls and not query:
            urls = [url for url in urls if url.strip()]  # Remove empty URLs

            if urls:
                try:
                    # Validate URLs
                    valid_urls = [url for url in urls if is_url_valid(url)]
                    if not valid_urls:
                        return JsonResponse({"error": "No valid URLs provided."}, status=400)

                    # Load data from URLs
                    data = load_urls(valid_urls)

                    # Filter and process data
                    for doc in data:
                        doc.page_content = filter_irrelevant_text(doc.page_content)

                    # Split text into chunks
                    text_splitter = RecursiveCharacterTextSplitter(separators=['\n\n', '\n', '.', ','], chunk_size=1000)
                    docs = text_splitter.split_documents(data)

                    # Create embeddings and store in FAISS
                    embeddings = get_huggingface_embeddings()
                    vectorstore = FAISS.from_documents(docs, embeddings)

                    # Save FAISS index for later use
                    with open(preloaded_faiss_path, "wb") as f:
                        pickle.dump(vectorstore, f)
                    
                    chat_session = ChatSession(user=request.user)
                    chat_session.save()

                    return JsonResponse({"message": "URLs processed successfully!"})
                except Exception as e:
                    return JsonResponse({"error": f"Error processing URLs: {e}"}, status=500)

        # Processing Query (if provided)
        elif query:
            if not os.path.exists(preloaded_faiss_path):
                return JsonResponse({"error": "No vectorstore available. Please process URLs first."}, status=400)

            try:
                # Load FAISS index
                with open(preloaded_faiss_path, "rb") as f:
                    vectorstore = pickle.load(f)

                # Retrieve relevant documents
                retriever = vectorstore.as_retriever()
                docs = retriever.get_relevant_documents(query)

                if not any(doc.page_content.strip() for doc in docs):
                    return JsonResponse({"error": "No meaningful content found in the provided URLs."}, status=400)

                # Prepare prompt for LLM
                documents_text = "\n".join([doc.page_content for doc in docs])
                prompt = f"Based on the following articles, answer the question: {query}\n\nArticles:\n{documents_text}"

                # Generate response using LLM
                response = llm.invoke(prompt)
                answer = response.content.strip()

                chat_session = ChatSession.objects.filter(user=request.user).order_by('-timestamp').first()
                if not chat_session:
                    chat_session = ChatSession(user=request.user)
                    chat_session.save()
                chatHistory = ChatHistory(
                    user=request.user,
                    session=chat_session,
                    mode="process_urls",
                    user_input=query,
                    response=answer
                )
                chatHistory.save()

                return JsonResponse({"answer": answer})
            except Exception as e:
                return JsonResponse({"error": f"Error processing query: {e}"}, status=500)

    return render(request, 'process_urls.html')

import logging
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json

logger = logging.getLogger(__name__)
MAX_CHAT_HISTORY = 50  # Limit chat history to prevent session bloat

@login_required
@csrf_exempt
def chat_companion(request):
    # Get the most recent chat session or create a new one
    chat_session = ChatSession.objects.filter(user=request.user).order_by('-timestamp').first()
    if not chat_session:
        chat_session = ChatSession(user=request.user)
        chat_session.save()

    # Fetch the last 10 chat history records for context
    chat_history_qs = ChatHistory.objects.filter(user=request.user,mode="chat_companion", session=chat_session).order_by('-timestamp')
    chat_history = list(reversed(chat_history_qs))  # Reverse to get chronological order

    response_text = ""

    if request.method == 'POST':
        content_type = request.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            try:
                data = json.loads(request.body)
                if data.get('message') == 'new page':
                    print("✅ New page view tracked!")
                    cs = ChatSession(user=request.user)
                    cs.save()
                    return JsonResponse({'status': 'success'})
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        query = request.POST.get('query', '').strip()
        print("query", query)
        if query:
            try:
                # Build message context for the LLM
                messages = [{"role": "system", "content": "You are a helpful assistant."}]
                for item in chat_history:
                    messages.append({"role": "user", "content": item.user_input})
                    messages.append({"role": "assistant", "content": item.response})
                messages.append({"role": "user", "content": query})

                # Call the LLM
                response = llm.invoke(messages)
                response_text = getattr(response, 'content', '').strip()

                # Save to ChatHistory
                ChatHistory.objects.create(
                    user=request.user,
                    session=chat_session,
                    mode="chat_companion",
                    user_input=query,
                    response=response_text
                )

            except Exception as e:
                logger.error(f"Error invoking LLM: {e}")
                response_text = "An error occurred. Please try again."

                # Save error response to ChatHistory
                ChatHistory.objects.create(
                    user=request.user,
                    session=chat_session,
                    mode="chat_companion",
                    user_input=query,
                    response=response_text
                )

        return JsonResponse({'response': response_text})

    # Prepare chat history for rendering
    chat_history_display = [
        {'query': item.user_input, 'response': item.response}
        for item in chat_history
    ]

    return render(request, 'chat_companion.html', {'chat_history': chat_history_display})

@login_required
def memory_bank(request):
    history = ChatHistory.objects.filter(user=request.user)
    return render(request, 'memory_bank.html', {'history': history})

# Utility Functions
def is_url_valid(url):
    try:
        print("url valid",url)
        if(url!=""):
            print("entered if")
            response = requests.get(url)
            print("response",response.status_code)
       
        return response.status_code == 200
    except:
        return False

def extract_main_content(url):
    """
    Extract the main content from a URL using trafilatura.
    """
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        return trafilatura.extract(downloaded)
    return None

def load_urls(urls):
    
    documents = []
    for url in urls:
        content = extract_main_content(url)
        if content:
            documents.append(Document(page_content=content, metadata={"source": url}))
    return documents

def filter_irrelevant_text(text):
    
    irrelevant_phrases = ["Advertisement", "Menu", "Sign up", "Privacy Policy"]
    for phrase in irrelevant_phrases:
        text = re.sub(f".{phrase}.\n?", "", text)
    return text

# Define Hugging Face Embeddings API with error handling
def get_huggingface_embeddings():
    try:
        return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    except Exception as e:
        print(f"Error: {e}")
        return None

from django.db.models import OuterRef, Subquery, Exists

@login_required
def ai_memory_bank(request):
    # Get all chat sessions for the user
    user_sessions = ChatSession.objects.filter(user=request.user)

    # Identify sessions without any related chat history
    sessions_without_history = user_sessions.annotate(
        has_history=Exists(ChatHistory.objects.filter(session=OuterRef('pk')))
    ).filter(has_history=False)

    # Delete those sessions
    sessions_without_history.delete()

    # Refresh the list of sessions and chat history after deletion
    chat_sessions = ChatSession.objects.filter(user=request.user).order_by('-timestamp')
    chat_history = ChatHistory.objects.filter(session__in=chat_sessions).order_by('-timestamp')

    return render(request, 'Memory_bank.html', {
        'history': chat_history,
        'sessions': chat_sessions
    })
def delete_chat_turn(request):
    if request.method == 'POST':
        history_id = request.POST.get('history_id')

        try:
            chat_turn = ChatHistory.objects.get(id=history_id)
            chat_turn.delete()
            return JsonResponse({'success': True})
        except ChatHistory.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Chat turn not found'})

    return JsonResponse({'success': False, 'message': 'Invalid request'})

