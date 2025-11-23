# Chatbot Stand - Real-time AI Assistant with Animated Avatar

A real-time chatbot system with an animated male avatar, designed for stand/booth displays. Features WebSocket-based streaming for low-latency voice and text interactions.

## Features

- **Animated Avatar**: Real-time mouth animation synchronized with speech (male and female options)
- **GPU-Accelerated**: Optimized for NVIDIA GPUs with automatic detection and fallback
- **Real-time Communication**: WebSocket-based streaming for instant responses
- **Multi-provider Support**:
  - **ASR (Speech Recognition)**: Faster-Whisper (GPU-optimized), WhisperX (advanced), Vosk
  - **TTS (Text-to-Speech)**: OpenAI, Google Cloud
  - **LLM (Language Model)**: OpenAI GPT, Google Gemini
- **Voice Interaction**: Push-to-talk voice input with real-time transcription
- **Streaming Responses**: Token-by-token text generation with streaming audio
- **Configurable**: All settings managed through `config.yaml`

## Architecture

```
chatbot_stand/
├── backend/
│   ├── config_loader.py      # Configuration management
│   ├── asr_module.py          # Speech recognition
│   ├── tts_module.py          # Text-to-speech
│   ├── llm_module.py          # Language model
│   └── websocket_server.py    # WebSocket server
├── frontend/
│   └── index.html             # Main HTML page
├── static/
│   ├── css/
│   │   └── style.css          # Styling
│   └── js/
│       ├── avatar.js          # Avatar animation
│       ├── websocket.js       # WebSocket client
│       └── main.js            # Main application logic
├── config.yaml                # Configuration file
└── requirements.txt           # Python dependencies
```

## Installation

### 1. GPU Setup (REQUIRED for optimal performance)

**⚠️ IMPORTANT: Install GPU support first for best performance!**

This system is optimized for NVIDIA GPUs. See [GPU_SETUP.md](GPU_SETUP.md) for detailed instructions.

**Quick GPU Setup:**
```bash
# Install PyTorch with CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify CUDA is available
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

### 2. Clone the Repository

```bash
git clone <repository-url>
cd chatbot_stand
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

The system will automatically:
- Detect your GPU and use it if available
- Download Whisper models on first run (~1.5GB for medium model)
- Use GPU-optimized faster-whisper for best performance

### 4. Configure API Keys

Edit `config.yaml` and add your API keys:

```yaml
# For OpenAI TTS and LLM
tts:
  openai:
    api_key: "your-openai-api-key-here"

llm:
  openai:
    api_key: "your-openai-api-key-here"

# For Google TTS (optional)
tts:
  google:
    credentials_path: "path/to/google-credentials.json"

# For Google Gemini LLM (optional)
llm:
  google:
    api_key: "your-google-api-key-here"
```

## Configuration

### config.yaml Structure

```yaml
# ASR Provider: whisper_local, whisperx_local (advanced), or vosk_local
asr:
  provider: "whisper_local"  # Use whisperx_local for word-level timestamps
  whisper:
    model: "medium"  # tiny, base, small, medium, large, large-v3
    language: "en"
    device: "auto"  # auto (recommended), cuda, cpu
    compute_type: "float16"  # float16 (GPU), int8, float32

# TTS Provider: openai or google
tts:
  provider: "openai"
  openai:
    model: "tts-1"  # tts-1 or tts-1-hd
    voice: "alloy"  # alloy, echo, fable, onyx, nova, shimmer
    speed: 1.0

# LLM Provider: openai or google
llm:
  provider: "openai"
  openai:
    model: "gpt-4o"  # gpt-4o, gpt-4-turbo, gpt-3.5-turbo
    temperature: 0.7
    max_tokens: 2000

# Avatar settings
avatar:
  gender: "male"  # male or female
  background_color: "#FFFFFF"
  mouth_animation: true
```

**Avatar Options:**
- `gender: "male"` or `gender: "female"` - Choose avatar appearance
- Avatar features: Animated mouth sync, natural blinking, gender-specific styling

**GPU Configuration:**
- `device: "auto"` - Automatically detects and uses GPU if available
- `compute_type: "float16"` - Uses FP16 precision for 2x faster GPU inference
- `model: "medium"` - Good balance of speed and accuracy for GPU (6GB VRAM)

See [GPU_SETUP.md](GPU_SETUP.md) for model recommendations based on your GPU memory.

## Usage

### Start the Server

```bash
python backend/websocket_server.py
```

Or specify a custom config file:

```bash
python backend/websocket_server.py /path/to/config.yaml
```

### Access the Web Interface

Open your browser and navigate to:
```
http://localhost:8000
```

### Interaction Methods

1. **Text Input**: Type your message in the input field and press Enter or click Send
2. **Voice Input**: Press and hold the microphone button, speak, then release to send

## API Reference

### WebSocket Protocol

The WebSocket endpoint is available at `/ws`. Messages are JSON-formatted.

#### Client to Server

**Text Message:**
```json
{
  "type": "text",
  "message": "Your message here"
}
```

**Audio Message:**
```json
{
  "type": "audio",
  "audio": "base64-encoded-audio-data"
}
```

#### Server to Client

**Text Chunk (Streaming):**
```json
{
  "type": "text_chunk",
  "text": "Token chunk"
}
```

**Audio Chunk (Streaming):**
```json
{
  "type": "audio_chunk",
  "audio": "base64-encoded-audio-data"
}
```

**Transcription:**
```json
{
  "type": "transcription",
  "text": "Transcribed text"
}
```

**Speaking Events:**
```json
{"type": "speaking_start"}
{"type": "speaking_end"}
```

## Model Options

### ASR Models

**Whisper (Local)**:
- `tiny`: Fastest, least accurate (~1GB RAM)
- `base`: Good balance (~1GB RAM)
- `small`: Better accuracy (~2GB RAM)
- `medium`: High accuracy (~5GB RAM)
- `large`: Best accuracy (~10GB RAM)

**Vosk (Local)**:
- Download models from: https://alphacephei.com/vosk/models
- Lightweight and fast for real-time transcription

### TTS Voices

**OpenAI**:
- `alloy`: Neutral
- `echo`: Male
- `fable`: British accent
- `onyx`: Deep male
- `nova`: Female
- `shimmer`: Soft female

**Google Cloud**:
- Many neural voices available
- Configured via `voice_name` in config.yaml

### LLM Models

**OpenAI**:
- `gpt-4o`: Latest, most capable
- `gpt-4-turbo`: Fast and capable
- `gpt-3.5-turbo`: Fast and cost-effective

**Google Gemini**:
- `gemini-1.5-pro`: Most capable
- `gemini-1.5-flash`: Faster, cost-effective

## Troubleshooting

### Microphone Access Denied
- Ensure your browser has microphone permissions
- HTTPS is required for microphone access in production
- Use `localhost` for development

### WebSocket Connection Failed
- Check that the server is running
- Verify firewall settings
- Ensure port 8000 is not in use

### Module Import Errors
- Run `pip install -r requirements.txt`
- Check Python version (3.8+ required)

### TTS/LLM API Errors
- Verify API keys in config.yaml
- Check API quota and billing
- Ensure internet connectivity

### GPU Support for Whisper
```bash
# Install PyTorch with CUDA support first
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Then change device in config.yaml
asr:
  whisper:
    device: "cuda"
```

## Performance Tips

1. **Use appropriate model sizes**: Start with smaller models and scale up as needed
2. **Enable GPU**: Use CUDA for Whisper if available
3. **Optimize TTS**: Use `tts-1` instead of `tts-1-hd` for faster responses
4. **Adjust streaming**: Balance between latency and quality

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.

## Credits

- Avatar animation: Custom canvas-based rendering
- ASR: OpenAI Whisper, Vosk
- TTS: OpenAI, Google Cloud
- LLM: OpenAI GPT, Google Gemini
