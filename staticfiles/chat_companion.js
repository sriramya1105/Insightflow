document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('chat-form');
    const chatBox = document.getElementById('chat-box');
    const chatHistory = document.getElementById('chat-history');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const input = document.getElementById('query-input');
        const userMessage = input.value.trim();

        if (userMessage) {
            // Display user message
            const userDiv = document.createElement('div');
            userDiv.className = 'user-message';
            userDiv.textContent = userMessage;
            chatBox.appendChild(userDiv);

            // AJAX request to send message to backend
            const response = await fetch(window.location.href, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: `query=${encodeURIComponent(userMessage)}`
            });

            const responseData = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(responseData, 'text/html');

            const newBotMessage = doc.querySelector('.bot-message');
            if (newBotMessage) {
                chatBox.appendChild(newBotMessage);
            }

            // Add to chat history sidebar
            const newHistoryItem = document.createElement('li');
            newHistoryItem.textContent = userMessage;
            chatHistory.appendChild(newHistoryItem);

            // Scroll to bottom
            chatBox.scrollTop = chatBox.scrollHeight;

            input.value = '';  // Clear input field
        }
    });
});
