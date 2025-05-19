document.addEventListener('DOMContentLoaded', function() {
    // Auto-scroll message container to bottom
    const messageContainer = document.querySelector('.message-container');
    if (messageContainer) {
        messageContainer.scrollTop = messageContainer.scrollHeight;
    }
    
    // Set up automatic fading for flash messages
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Set up confirmation for clearing conversations
    const clearButtons = document.querySelectorAll('.clear-conversation');
    clearButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to clear this conversation? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
    
    // Detect Persian/Farsi text for RTL layout
    const messages = document.querySelectorAll('.message');
    messages.forEach(function(message) {
        const text = message.textContent;
        const persianPattern = /[\u0600-\u06FF]/;
        if (persianPattern.test(text)) {
            message.classList.add('rtl');
        }
    });
    
    // Handle user selection in conversation list
    const userItems = document.querySelectorAll('.user-item');
    userItems.forEach(function(item) {
        item.addEventListener('click', function() {
            const userId = this.getAttribute('data-user-id');
            window.location.href = `/conversation/${userId}`;
        });
    });
});
