/**
 * WebSocket communication module
 */

class ChatWebSocket {
    constructor(url) {
        this.url = url;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.messageHandlers = [];
        this.statusHandlers = [];
        this.audioChunks = [];
        this.mediaRecorder = null;
        this.isRecording = false;

        this.connect();
    }

    /**
     * Connect to WebSocket server
     */
    connect() {
        try {
            this.ws = new WebSocket(this.url);

            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.reconnectAttempts = 0;
                this.notifyStatus('connected');
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('Error parsing message:', error);
                }
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.notifyStatus('error');
            };

            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.notifyStatus('disconnected');
                this.attemptReconnect();
            };
        } catch (error) {
            console.error('Error creating WebSocket:', error);
            this.attemptReconnect();
        }
    }

    /**
     * Attempt to reconnect to WebSocket server
     */
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);

            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            console.error('Max reconnection attempts reached');
            this.notifyStatus('failed');
        }
    }

    /**
     * Handle incoming WebSocket message
     */
    handleMessage(data) {
        this.messageHandlers.forEach(handler => handler(data));
    }

    /**
     * Add message handler
     */
    onMessage(handler) {
        this.messageHandlers.push(handler);
    }

    /**
     * Add status change handler
     */
    onStatusChange(handler) {
        this.statusHandlers.push(handler);
    }

    /**
     * Notify status change
     */
    notifyStatus(status) {
        this.statusHandlers.forEach(handler => handler(status));
    }

    /**
     * Send text message
     */
    sendText(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'text',
                message: message
            }));
        } else {
            console.error('WebSocket not connected');
        }
    }

    /**
     * Send audio data
     */
    sendAudio(audioData) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'audio',
                audio: audioData
            }));
        } else {
            console.error('WebSocket not connected');
        }
    }

    /**
     * Start audio recording
     */
    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    sampleRate: 16000,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true
                }
            });

            this.audioChunks = [];
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm'
            });

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                const audioBase64 = await this.blobToBase64(audioBlob);

                // Send audio to server
                this.sendAudio(audioBase64);

                // Stop all tracks
                stream.getTracks().forEach(track => track.stop());
            };

            this.mediaRecorder.start();
            this.isRecording = true;

            return true;
        } catch (error) {
            console.error('Error starting recording:', error);
            alert('Microphone access denied. Please allow microphone access to use voice input.');
            return false;
        }
    }

    /**
     * Stop audio recording
     */
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
        }
    }

    /**
     * Convert blob to base64
     */
    async blobToBase64(blob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => {
                const base64 = reader.result.split(',')[1];
                resolve(base64);
            };
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    }

    /**
     * Send ping to keep connection alive
     */
    ping() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type: 'ping' }));
        }
    }

    /**
     * Close WebSocket connection
     */
    close() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

// Export for use in main.js
window.ChatWebSocket = ChatWebSocket;
