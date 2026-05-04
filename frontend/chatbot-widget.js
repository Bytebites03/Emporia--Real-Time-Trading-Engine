// Chatbot Widget for Trading Interface
class TradingChatbot {
    constructor() {
        this.isOpen = false;
        this.userId = 'chat_' + Math.random().toString(36).substr(2, 9);
        this.ws = null;
        this.messageHistory = [];
        this.init();
    }
    
    init() {
        this.createWidget();
        this.connectWebSocket();
        this.bindEvents();
    }
    
    createWidget() {
        // Create chatbot container
        const chatbotHTML = `
            <div id="chatbotWidget" class="chatbot-widget">
                <div class="chatbot-header" id="chatbotHeader">
                    <div class="chatbot-header-content">
                        <span class="chatbot-icon">🤖</span>
                        <div>
                            <h3>Finance Tutor</h3>
                            <p>Learn trading & use the app</p>
                        </div>
                    </div>
                    <button class="chatbot-toggle" id="chatbotToggle">
                        <span class="toggle-icon">💬</span>
                    </button>
                </div>
                
                <div class="chatbot-body" id="chatbotBody" style="display: none;">
                    <div class="chatbot-messages" id="chatbotMessages">
                        <div class="message bot-message">
                            <div class="message-avatar">🤖</div>
                            <div class="message-content">
                                <p>👋 Hello! I'm your personal trading tutor!</p>
                                <p>I can teach you:</p>
                                <ul>
                                    <li>📚 Trading concepts (limit/market orders)</li>
                                    <li>📊 How to read charts and order books</li>
                                    <li>🎯 Step-by-step app tutorials</li>
                                    <li>⚠️ Risk management strategies</li>
                                </ul>
                                <p>Try asking: <em>"How to place first trade?"</em> or <em>"What is a limit order?"</em></p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="chatbot-suggestions" id="chatbotSuggestions">
                        <button class="suggestion-btn">What is a limit order?</button>
                        <button class="suggestion-btn">How to place first trade?</button>
                        <button class="suggestion-btn">What is risk management?</button>
                    </div>
                    
                    <div class="chatbot-input-area">
                        <input type="text" id="chatbotInput" placeholder="Ask me anything about trading..." />
                        <button id="chatbotSend" class="send-btn">Send</button>
                    </div>
                    
                    <div class="chatbot-status">
                        <span class="status-indicator"></span>
                        <span>AI Tutor • Always learning</span>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', chatbotHTML);
        
        // Add styles
        this.addStyles();
    }
    
    addStyles() {
        const styles = `
            <style>
                .chatbot-widget {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    width: 380px;
                    background: #1a1f3a;
                    border-radius: 12px;
                    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
                    border: 1px solid #2a2f4a;
                    z-index: 1000;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                }
                
                .chatbot-header {
                    padding: 15px;
                    background: linear-gradient(135deg, #2a2f4a, #1a1f3a);
                    border-radius: 12px 12px 0 0;
                    cursor: pointer;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .chatbot-header-content {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }
                
                .chatbot-icon {
                    font-size: 28px;
                }
                
                .chatbot-header h3 {
                    margin: 0;
                    font-size: 16px;
                    color: #4caf50;
                }
                
                .chatbot-header p {
                    margin: 0;
                    font-size: 11px;
                    color: #888;
                }
                
                .chatbot-toggle {
                    background: none;
                    border: none;
                    color: #e0e0e0;
                    font-size: 20px;
                    cursor: pointer;
                    padding: 5px 10px;
                }
                
                .chatbot-body {
                    display: none;
                    flex-direction: column;
                    height: 500px;
                }
                
                .chatbot-body.open {
                    display: flex;
                }
                
                .chatbot-messages {
                    flex: 1;
                    overflow-y: auto;
                    padding: 15px;
                    background: #0f1428;
                }
                
                .message {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 15px;
                    animation: slideIn 0.3s ease;
                }
                
                @keyframes slideIn {
                    from {
                        opacity: 0;
                        transform: translateY(10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                
                .user-message {
                    flex-direction: row-reverse;
                }
                
                .message-avatar {
                    width: 32px;
                    height: 32px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 18px;
                    background: #2a2f4a;
                }
                
                .message-content {
                    max-width: 70%;
                    padding: 10px;
                    border-radius: 12px;
                    font-size: 13px;
                    line-height: 1.5;
                }
                
                .bot-message .message-content {
                    background: #1a1f3a;
                    color: #e0e0e0;
                }
                
                .user-message .message-content {
                    background: #4caf50;
                    color: white;
                }
                
                .message-content p {
                    margin: 0 0 5px 0;
                }
                
                .message-content ul {
                    margin: 5px 0;
                    padding-left: 20px;
                }
                
                .message-content li {
                    margin: 3px 0;
                }
                
                .chatbot-suggestions {
                    padding: 10px;
                    display: flex;
                    gap: 8px;
                    overflow-x: auto;
                    background: #0f1428;
                    border-top: 1px solid #2a2f4a;
                }
                
                .suggestion-btn {
                    padding: 6px 12px;
                    background: #2a2f4a;
                    border: 1px solid #4caf50;
                    border-radius: 20px;
                    color: #4caf50;
                    font-size: 11px;
                    cursor: pointer;
                    white-space: nowrap;
                    transition: all 0.2s;
                }
                
                .suggestion-btn:hover {
                    background: #4caf50;
                    color: white;
                }
                
                .chatbot-input-area {
                    padding: 10px;
                    display: flex;
                    gap: 8px;
                    background: #0f1428;
                    border-top: 1px solid #2a2f4a;
                }
                
                #chatbotInput {
                    flex: 1;
                    padding: 8px 12px;
                    background: #1a1f3a;
                    border: 1px solid #2a2f4a;
                    border-radius: 6px;
                    color: #e0e0e0;
                    font-size: 13px;
                }
                
                #chatbotInput:focus {
                    outline: none;
                    border-color: #4caf50;
                }
                
                .send-btn {
                    padding: 8px 16px;
                    background: #4caf50;
                    border: none;
                    border-radius: 6px;
                    color: white;
                    cursor: pointer;
                    font-weight: bold;
                }
                
                .send-btn:hover {
                    background: #45a049;
                }
                
                .chatbot-status {
                    padding: 8px;
                    text-align: center;
                    font-size: 10px;
                    color: #888;
                    background: #0f1428;
                    border-top: 1px solid #2a2f4a;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 6px;
                }
                
                .status-indicator {
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: #4caf50;
                    animation: pulse 2s infinite;
                }
                
                .typing-indicator {
                    display: flex;
                    gap: 4px;
                    padding: 10px;
                }
                
                .typing-indicator span {
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: #888;
                    animation: typing 1.4s infinite;
                }
                
                .typing-indicator span:nth-child(2) {
                    animation-delay: 0.2s;
                }
                
                .typing-indicator span:nth-child(3) {
                    animation-delay: 0.4s;
                }
                
                @keyframes typing {
                    0%, 60%, 100% {
                        transform: translateY(0);
                        opacity: 0.4;
                    }
                    30% {
                        transform: translateY(-10px);
                        opacity: 1;
                    }
                }
                
                @media (max-width: 768px) {
                    .chatbot-widget {
                        width: 100%;
                        bottom: 0;
                        right: 0;
                        border-radius: 12px 12px 0 0;
                    }
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }
    
    connectWebSocket() {
        const wsUrl = `ws://localhost:8000/ws/chat/${this.userId}`;
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('Chatbot connected');
            this.updateStatus(true);
        };
        
        this.ws.onmessage = (event) => {
            const response = JSON.parse(event.data);
            this.addBotMessage(response.answer);
            
            // Update suggestions if provided
            if (response.suggestions && response.suggestions.length > 0) {
                this.updateSuggestions(response.suggestions);
            }
        };
        
        this.ws.onerror = (error) => {
            console.error('Chatbot WebSocket error:', error);
            this.updateStatus(false);
        };
        
        this.ws.onclose = () => {
            console.log('Chatbot disconnected');
            this.updateStatus(false);
            setTimeout(() => this.connectWebSocket(), 3000);
        };
    }
    
    bindEvents() {
        // Toggle chatbot
        const toggleBtn = document.getElementById('chatbotToggle');
        const header = document.getElementById('chatbotHeader');
        const body = document.getElementById('chatbotBody');
        
        const toggle = () => {
            this.isOpen = !this.isOpen;
            body.style.display = this.isOpen ? 'flex' : 'none';
            const icon = toggleBtn.querySelector('.toggle-icon');
            if (icon) icon.textContent = this.isOpen ? '✕' : '💬';
        };
        
        toggleBtn.addEventListener('click', toggle);
        header.addEventListener('click', (e) => {
            if (e.target !== toggleBtn && !toggleBtn.contains(e.target)) {
                toggle();
            }
        });
        
        // Send message
        const sendBtn = document.getElementById('chatbotSend');
        const input = document.getElementById('chatbotInput');
        
        const sendMessage = () => {
            const text = input.value.trim();
            if (text && this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.addUserMessage(text);
                this.ws.send(JSON.stringify({ text: text }));
                input.value = '';
                this.showTyping();
            }
        };
        
        sendBtn.addEventListener('click', sendMessage);
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
        
        // Suggestion buttons
        document.getElementById('chatbotSuggestions').addEventListener('click', (e) => {
            if (e.target.classList.contains('suggestion-btn')) {
                const question = e.target.textContent;
                document.getElementById('chatbotInput').value = question;
                sendMessage();
            }
        });
    }
    
    addUserMessage(text) {
        const messagesContainer = document.getElementById('chatbotMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.innerHTML = `
            <div class="message-avatar">👤</div>
            <div class="message-content">
                <p>${this.escapeHtml(text)}</p>
            </div>
        `;
        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addBotMessage(text) {
        const messagesContainer = document.getElementById('chatbotMessages');
        
        // Remove typing indicator if present
        const typingIndicator = messagesContainer.querySelector('.typing-indicator');
        if (typingIndicator) typingIndicator.remove();
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';
        messageDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                ${this.formatMessage(text)}
            </div>
        `;
        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatMessage(text) {
        // Convert markdown-style formatting
        let formatted = text;
        
        // Bold
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Line breaks
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Lists
        formatted = formatted.replace(/- (.*?)(<br>|$)/g, '<li>$1</li>');
        formatted = formatted.replace(/<li>.*?<\/li>/g, '<ul>$&</ul>');
        
        // Emojis are already there
        return formatted;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    showTyping() {
        const messagesContainer = document.getElementById('chatbotMessages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.innerHTML = '<span></span><span></span><span></span>';
        messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    updateSuggestions(suggestions) {
        const suggestionsContainer = document.getElementById('chatbotSuggestions');
        suggestionsContainer.innerHTML = '';
        suggestions.forEach(suggestion => {
            const btn = document.createElement('button');
            btn.className = 'suggestion-btn';
            btn.textContent = suggestion;
            suggestionsContainer.appendChild(btn);
        });
    }
    
    updateStatus(connected) {
        const indicator = document.querySelector('.status-indicator');
        if (indicator) {
            indicator.style.background = connected ? '#4caf50' : '#ff4444';
        }
    }
    
    scrollToBottom() {
        const messagesContainer = document.getElementById('chatbotMessages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

// Initialize chatbot when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new TradingChatbot();
});