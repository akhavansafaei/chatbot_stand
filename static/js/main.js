/**
 * Main application logic
 */

class ChatbotApp {
    constructor() {
        // Initialize avatar
        this.avatar = new Avatar('avatarCanvas');

        // Initialize WebSocket
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        this.ws = new ChatWebSocket(wsUrl);

        // DOM elements
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.recordBtn = document.getElementById('recordBtn');
        this.statusDot = document.getElementById('statusDot');
        this.statusText = document.getElementById('statusText');
        this.transcriptionPreview = document.getElementById('transcriptionPreview');
        this.audioPlayer = document.getElementById('audioPlayer');

        // State
        this.isProcessing = false;
        this.currentAudioChunks = [];
        this.mediaSource = null;
        this.sourceBuffer = null;

        // Setup event listeners
        this.setupEventListeners();

        // Setup WebSocket handlers
        this.setupWebSocketHandlers();

        // Keep-alive ping
        setInterval(() => this.ws.ping(), 30000);
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Send button
        this.sendBtn.addEventListener('click', () => this.sendMessage());

        // Enter key to send
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Record button
        this.recordBtn.addEventListener('mousedown', () => this.startRecording());
        this.recordBtn.addEventListener('mouseup', () => this.stopRecording());
        this.recordBtn.addEventListener('mouseleave', () => {
            if (this.ws.isRecording) {
                this.stopRecording();
            }
        });

        // Touch events for mobile
        this.recordBtn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.startRecording();
        });
        this.recordBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.stopRecording();
        });
    }

    /**
     * Setup WebSocket message handlers
     */
    setupWebSocketHandlers() {
        // Status changes
        this.ws.onStatusChange((status) => {
            this.updateStatus(status);
        });

        // Messages
        this.ws.onMessage((data) => {
            switch (data.type) {
                case 'system':
                    this.addSystemMessage(data.message);
                    break;

                case 'config':
                    // Apply avatar configuration
                    if (data.avatar) {
                        if (data.avatar.gender) {
                            this.avatar.setGender(data.avatar.gender);
                        }
                        if (data.avatar.background_color) {
                            this.canvas.style.backgroundColor = data.avatar.background_color;
                        }
                    }
                    break;

                case 'text_chunk':
                    this.appendToLastMessage(data.text);
                    break;

                case 'transcription':
                    this.showTranscription(data.text);
                    break;

                case 'audio_chunk':
                    this.playAudioChunk(data.audio);
                    break;

                case 'speaking_start':
                    this.avatar.setSpeaking(true);
                    this.updateStatus('speaking');
                    this.addAssistantMessage('');
                    break;

                case 'speaking_end':
                    this.avatar.setSpeaking(false);
                    this.updateStatus('connected');
                    this.isProcessing = false;
                    break;

                case 'error':
                    this.addErrorMessage(data.message);
                    this.isProcessing = false;
                    this.avatar.setSpeaking(false);
                    break;

                case 'pong':
                    // Keep-alive response
                    break;
            }
        });
    }

    /**
     * Update connection status
     */
    updateStatus(status) {
        this.statusDot.className = `status-dot ${status}`;

        switch (status) {
            case 'connected':
                this.statusText.textContent = 'Connected';
                break;
            case 'disconnected':
                this.statusText.textContent = 'Disconnected';
                break;
            case 'speaking':
                this.statusText.textContent = 'Speaking...';
                break;
            case 'error':
                this.statusText.textContent = 'Error';
                break;
            case 'failed':
                this.statusText.textContent = 'Connection Failed';
                break;
        }
    }

    /**
     * Send text message
     */
    sendMessage() {
        const message = this.messageInput.value.trim();

        if (!message || this.isProcessing) {
            return;
        }

        // Add user message to chat
        this.addUserMessage(message);

        // Clear input
        this.messageInput.value = '';

        // Send to server
        this.ws.sendText(message);
        this.isProcessing = true;
    }

    /**
     * Start recording audio
     */
    async startRecording() {
        if (this.isProcessing) {
            return;
        }

        const started = await this.ws.startRecording();

        if (started) {
            this.recordBtn.classList.add('recording');
            this.transcriptionPreview.textContent = 'Recording... Release to send';
        }
    }

    /**
     * Stop recording audio
     */
    stopRecording() {
        this.ws.stopRecording();
        this.recordBtn.classList.remove('recording');
        this.transcriptionPreview.textContent = 'Processing...';
        this.isProcessing = true;
    }

    /**
     * Show transcription preview
     */
    showTranscription(text) {
        this.transcriptionPreview.textContent = `You said: "${text}"`;

        setTimeout(() => {
            this.transcriptionPreview.textContent = '';
        }, 3000);
    }

    /**
     * Add user message to chat
     */
    addUserMessage(text) {
        const messageDiv = this.createMessageElement('user', text);
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    /**
     * Add assistant message to chat
     */
    addAssistantMessage(text) {
        const messageDiv = this.createMessageElement('assistant', text);
        messageDiv.setAttribute('data-message-id', 'latest');
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    /**
     * Append text to last assistant message
     */
    appendToLastMessage(text) {
        const lastMessage = this.chatMessages.querySelector('[data-message-id="latest"]');

        if (lastMessage) {
            const bubble = lastMessage.querySelector('.message-bubble');
            bubble.textContent += text;
            this.scrollToBottom();
        }
    }

    /**
     * Add system message to chat
     */
    addSystemMessage(text) {
        const messageDiv = this.createMessageElement('system', text);
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    /**
     * Add error message to chat
     */
    addErrorMessage(text) {
        const messageDiv = this.createMessageElement('error', text);
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    /**
     * Create message element
     */
    createMessageElement(type, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.textContent = text;

        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = new Date().toLocaleTimeString();

        messageDiv.appendChild(bubble);
        messageDiv.appendChild(time);

        return messageDiv;
    }

    /**
     * Play audio chunk
     */
    async playAudioChunk(audioBase64) {
        try {
            // Decode base64 to blob
            const audioData = atob(audioBase64);
            const audioArray = new Uint8Array(audioData.length);

            for (let i = 0; i < audioData.length; i++) {
                audioArray[i] = audioData.charCodeAt(i);
            }

            const audioBlob = new Blob([audioArray], { type: 'audio/mpeg' });

            // Store chunks
            this.currentAudioChunks.push(audioBlob);

            // If this is the first chunk, start playing
            if (this.currentAudioChunks.length === 1) {
                this.playAudioChunks();
            }
        } catch (error) {
            console.error('Error playing audio chunk:', error);
        }
    }

    /**
     * Play accumulated audio chunks
     */
    async playAudioChunks() {
        if (this.currentAudioChunks.length === 0) {
            return;
        }

        // Combine all chunks
        const combinedBlob = new Blob(this.currentAudioChunks, { type: 'audio/mpeg' });
        const audioUrl = URL.createObjectURL(combinedBlob);

        // Play audio
        this.audioPlayer.src = audioUrl;

        try {
            await this.audioPlayer.play();

            // Clear chunks when done
            this.audioPlayer.onended = () => {
                this.currentAudioChunks = [];
                URL.revokeObjectURL(audioUrl);
            };
        } catch (error) {
            console.error('Error playing audio:', error);
        }
    }

    /**
     * Scroll chat to bottom
     */
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ChatbotApp();
});
