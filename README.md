🧠 InsightFlow: AI-Driven News & Query Companion

InsightFlow is an intelligent, modern AI system built with Django that helps users extract insights from URLs, chat with an AI companion, and store important knowledge in a powerful memory system.
Designed with a ChatGPT-like interface and a smooth user experience.

📸 Dashboard Preview

After you upload your dashboard image inside:

static/images/InsightFlow-Dashboard.png

![InsightFlow Dashboard](./static/diagram.jpg)

Add this in your README (already included below):


✨ Core Features
🔗 URL Processing

Extracts detailed content from any article/blog URL

Summarizes information

Detects emotion, sentiment & topics

Supports multilingual content

💬 Chat Companion

ChatGPT-style interface

Remembers context within the same session

Sidebar shows scrollable past chats

Guest mode → shows Login / Create Account option

🧠 AI Memory Bank

Stores important knowledge

Can be reused by the system for future responses

Maintains a clean memory JSON/DB structure

📰 Intelligent News Cards

Minimal cards → Only Image + Heading

Fetches real-time news

Category filtering

🧱 Project Structure

Your project structure (matching screenshot):

INSIGHTFLOW/
│── .github/
│── Insightflow/              # Django project folder
│── main/                     # Main Django app
│── static/
│     └── images/             # Dashboard & other images here
│── staticfiles/
│── templates/                # HTML templates
│── .gitattributes
│── chat_history.json         # Local session chat storage
│── db.sqlite3                # Database
│── faiss_index.pkl           # Memory vector index
│── manage.py
│── README.md
│── requirements.txt

🔧 Tech Stack
Backend

Django

Python

ChatGroq (Llama-3.1-70B)

FAISS for memory indexing

Frontend

HTML + CSS + JavaScript

ChatGPT-style UI layout

Scrollable chat sidebar

🚀 Setup Instructions
1️⃣ Clone Repo
git clone https://github.com/<your-username>/InsightFlow.git
cd InsightFlow

2️⃣ Create a Virtual Environment
python -m venv env
env\Scripts\activate      # Windows
source env/bin/activate   # Mac/Linux

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Set Environment Variables

Create .env inside the root folder:

GROQ_API_KEY=your_key
NEWS_API_KEY=your_key
SECRET_KEY=your_django_secret

5️⃣ Run Migrations
python manage.py migrate

6️⃣ Start Server
python manage.py runserver

🗂️ How It Works
✔ URL → Insights

Enter any article URL → system fetches → summarizes → displays insights.

✔ Personal Chat Companion

Behaves like ChatGPT inside your system.
Session memory only (no permanent storage unless user adds to Memory Bank).

✔ Memory Bank

Stores important entries into FAISS + DB.

✔ News Fetcher

Shows quick digest cards with images.

🛠️ Future Upgrades

PDF → Insights

Voice conversation support

Cross-session persistent chat

Enhanced news filtering

🤝 Contributing

PRs are welcome!
Feel free to open issues & feature requests.
