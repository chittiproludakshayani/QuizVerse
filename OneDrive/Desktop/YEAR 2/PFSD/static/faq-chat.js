// Simple chat widget for FAQ page
window.addEventListener('DOMContentLoaded', function() {
    const chatBox = document.getElementById('faq-chat-box');
    const chatInput = document.getElementById('faq-chat-input');
    const chatSend = document.getElementById('faq-chat-send');

    function appendMessage(sender, text) {
        const msg = document.createElement('div');
        msg.className = sender === 'user' ? 'chat-msg user' : 'chat-msg bot';
        msg.textContent = text;
        chatBox.appendChild(msg);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    chatSend.onclick = function() {
        const userMsg = chatInput.value.trim();
        if (!userMsg) return;
        appendMessage('user', userMsg);
        chatInput.value = '';
        // Simple bot response (expand with more logic or backend integration)
        setTimeout(function() {
            let response = "Sorry, I'm just a demo bot. Please contact support for complex queries.";
            if (/price|cost|market/i.test(userMsg)) response = "You can check crop prices on the Crop Prices page.";
            else if (/predict|recommend/i.test(userMsg)) response = "Use the Crop Yield Prediction page for recommendations.";
            else if (/feedback/i.test(userMsg)) response = "Submit your feedback on the Farmer Feedback page.";
            else if (/disease|plant|doctor/i.test(userMsg)) response = "Try the Crop Doctor page for plant disease analysis.";
            appendMessage('bot', response);
        }, 600);
    };

    chatInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') chatSend.onclick();
    });
});
