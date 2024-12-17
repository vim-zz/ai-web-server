document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('chatInput');
    const sendButton = document.getElementById('sendButton');
    const chatMessages = document.getElementById('chat-messages');
    const jsonDisplay = document.getElementById('json-display');

    // Add initial bot message
    addMessage("Hi! I'm here to help you register. Could you please tell me your name?", 'bot');
    updateJsonDisplay({
        name: null,
        username: null,
        password: null,
        workplace: null
    });

    function addMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        messageDiv.textContent = message;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function updateJsonDisplay(data) {
        // Create a display version of the data where password is masked if it exists
        const displayData = {...data};
        if (displayData.password) {
            displayData.password = '********';
        }
        jsonDisplay.textContent = JSON.stringify(displayData, null, 2);
    }

    async function sendMessage() {
        const message = chatInput.value.trim();
        if (message) {
            addMessage(message, 'user');
            chatInput.value = '';

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message }),
                });

                const data = await response.json();
                addMessage(data.message, 'bot');
                updateJsonDisplay(data.collected_info);

                if (data.registration_complete) {
                    addMessage("Registration completed successfully! Thank you for signing up.", 'bot');
                    chatInput.disabled = true;
                    sendButton.disabled = true;
                }
            } catch (error) {
                addMessage('Sorry, something went wrong. Please try again.', 'bot');
            }
        }
    }

    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
