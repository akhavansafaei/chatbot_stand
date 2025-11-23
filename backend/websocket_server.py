"""WebSocket server for real-time chatbot communication."""

import asyncio
import json
import base64
import logging
from typing import Set
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config_loader import ConfigLoader
from asr_module import ASRModule
from tts_module import TTSModule
from llm_module import LLMModule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChatbotServer:
    """WebSocket server for the chatbot."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the chatbot server.

        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config_loader = ConfigLoader(config_path)
        server_config = self.config_loader.get_server_config()

        # Initialize FastAPI app
        self.app = FastAPI(title="Chatbot Stand")

        # Initialize modules
        try:
            self.asr_module = ASRModule(self.config_loader.get_asr_config())
            logger.info("ASR module initialized")
        except Exception as e:
            logger.warning(f"ASR module initialization failed: {e}")
            self.asr_module = None

        try:
            self.tts_module = TTSModule(self.config_loader.get_tts_config())
            logger.info("TTS module initialized")
        except Exception as e:
            logger.warning(f"TTS module initialization failed: {e}")
            self.tts_module = None

        try:
            system_prompt = self.config_loader.get("system_prompt", "")
            self.llm_module = LLMModule(
                self.config_loader.get_llm_config(),
                system_prompt=system_prompt
            )
            logger.info("LLM module initialized")
        except Exception as e:
            logger.warning(f"LLM module initialization failed: {e}")
            self.llm_module = None

        # Active WebSocket connections
        self.active_connections: Set[WebSocket] = set()

        # Setup routes
        self._setup_routes()

    def _setup_routes(self):
        """Setup FastAPI routes."""
        # Serve static files
        static_path = Path(__file__).parent.parent / "static"
        if static_path.exists():
            self.app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

        # Serve frontend
        frontend_path = Path(__file__).parent.parent / "frontend"

        @self.app.get("/")
        async def serve_index():
            """Serve the main HTML page."""
            index_path = frontend_path / "index.html"
            if index_path.exists():
                return FileResponse(str(index_path))
            return {"message": "Frontend not found"}

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for chatbot communication."""
            await self.handle_websocket(websocket)

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "asr_available": self.asr_module is not None,
                "tts_available": self.tts_module is not None,
                "llm_available": self.llm_module is not None
            }

    async def handle_websocket(self, websocket: WebSocket):
        """Handle WebSocket connection.

        Args:
            websocket: WebSocket connection
        """
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"New WebSocket connection. Total connections: {len(self.active_connections)}")

        try:
            # Send initial greeting
            await websocket.send_json({
                "type": "system",
                "message": "Connected to chatbot server"
            })

            while True:
                # Receive message
                data = await websocket.receive_json()
                message_type = data.get("type")

                if message_type == "text":
                    # Handle text message
                    await self._handle_text_message(websocket, data)

                elif message_type == "audio":
                    # Handle audio message (ASR)
                    await self._handle_audio_message(websocket, data)

                elif message_type == "ping":
                    # Handle ping
                    await websocket.send_json({"type": "pong"})

        except WebSocketDisconnect:
            logger.info("WebSocket disconnected")
        except Exception as e:
            logger.error(f"WebSocket error: {e}", exc_info=True)
        finally:
            self.active_connections.discard(websocket)
            logger.info(f"Connection closed. Total connections: {len(self.active_connections)}")

    async def _handle_text_message(self, websocket: WebSocket, data: dict):
        """Handle text message from client.

        Args:
            websocket: WebSocket connection
            data: Message data
        """
        user_message = data.get("message", "")
        logger.info(f"Received text message: {user_message}")

        if not self.llm_module:
            await websocket.send_json({
                "type": "error",
                "message": "LLM module not available"
            })
            return

        try:
            # Generate LLM response with streaming
            full_response = ""

            # Start speaking event
            await websocket.send_json({"type": "speaking_start"})

            async for chunk in self.llm_module.generate_stream(user_message):
                full_response += chunk

                # Send text chunk
                await websocket.send_json({
                    "type": "text_chunk",
                    "text": chunk
                })

            # Generate TTS audio if available
            if self.tts_module and full_response:
                await self._generate_and_send_audio(websocket, full_response)

            # End speaking event
            await websocket.send_json({"type": "speaking_end"})

        except Exception as e:
            logger.error(f"Error handling text message: {e}", exc_info=True)
            await websocket.send_json({
                "type": "error",
                "message": f"Error processing message: {str(e)}"
            })

    async def _handle_audio_message(self, websocket: WebSocket, data: dict):
        """Handle audio message from client (ASR).

        Args:
            websocket: WebSocket connection
            data: Message data
        """
        if not self.asr_module:
            await websocket.send_json({
                "type": "error",
                "message": "ASR module not available"
            })
            return

        try:
            # Decode audio data
            audio_base64 = data.get("audio", "")
            audio_data = base64.b64decode(audio_base64)

            # Transcribe audio
            transcription = await self.asr_module.transcribe(audio_data)
            logger.info(f"Transcription: {transcription}")

            if transcription:
                # Send transcription to client
                await websocket.send_json({
                    "type": "transcription",
                    "text": transcription
                })

                # Process as text message
                await self._handle_text_message(websocket, {
                    "type": "text",
                    "message": transcription
                })

        except Exception as e:
            logger.error(f"Error handling audio message: {e}", exc_info=True)
            await websocket.send_json({
                "type": "error",
                "message": f"Error processing audio: {str(e)}"
            })

    async def _generate_and_send_audio(self, websocket: WebSocket, text: str):
        """Generate and send TTS audio.

        Args:
            websocket: WebSocket connection
            text: Text to synthesize
        """
        try:
            # Stream TTS audio
            async for audio_chunk in self.tts_module.synthesize_stream(text):
                # Encode audio chunk as base64
                audio_base64 = base64.b64encode(audio_chunk).decode('utf-8')

                # Send audio chunk
                await websocket.send_json({
                    "type": "audio_chunk",
                    "audio": audio_base64
                })

        except Exception as e:
            logger.error(f"Error generating TTS audio: {e}", exc_info=True)

    def run(self, host: str = None, port: int = None):
        """Run the server.

        Args:
            host: Host to bind to
            port: Port to bind to
        """
        import uvicorn

        server_config = self.config_loader.get_server_config()
        host = host or server_config.get("host", "0.0.0.0")
        port = port or server_config.get("port", 8000)

        logger.info(f"Starting server on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)


def main():
    """Main entry point."""
    import sys

    config_path = "config.yaml"
    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    server = ChatbotServer(config_path)
    server.run()


if __name__ == "__main__":
    main()
