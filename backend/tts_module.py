"""TTS (Text-to-Speech) module with API options."""

import io
import base64
from typing import AsyncGenerator
from abc import ABC, abstractmethod


class TTSProvider(ABC):
    """Abstract base class for TTS providers."""

    @abstractmethod
    async def synthesize(self, text: str) -> bytes:
        """Synthesize text to audio.

        Args:
            text: Text to synthesize

        Returns:
            Audio data in bytes
        """
        pass

    @abstractmethod
    async def synthesize_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        """Synthesize text to audio stream.

        Args:
            text: Text to synthesize

        Yields:
            Audio chunks
        """
        pass


class OpenAITTS(TTSProvider):
    """OpenAI TTS provider."""

    def __init__(self, api_key: str, model: str = "tts-1", voice: str = "alloy", speed: float = 1.0):
        """Initialize OpenAI TTS.

        Args:
            api_key: OpenAI API key
            model: TTS model name
            voice: Voice name
            speed: Speech speed
        """
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=api_key)
            self.model = model
            self.voice = voice
            self.speed = speed
        except ImportError:
            raise ImportError("Please install openai: pip install openai")

    async def synthesize(self, text: str) -> bytes:
        """Synthesize text to audio.

        Args:
            text: Text to synthesize

        Returns:
            Audio data in MP3 format
        """
        response = await self.client.audio.speech.create(
            model=self.model,
            voice=self.voice,
            input=text,
            speed=self.speed
        )

        # Read all content
        audio_data = b""
        async for chunk in response.iter_bytes():
            audio_data += chunk

        return audio_data

    async def synthesize_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        """Synthesize text to audio stream.

        Args:
            text: Text to synthesize

        Yields:
            Audio chunks in MP3 format
        """
        response = await self.client.audio.speech.create(
            model=self.model,
            voice=self.voice,
            input=text,
            speed=self.speed
        )

        async for chunk in response.iter_bytes():
            if chunk:
                yield chunk


class GoogleTTS(TTSProvider):
    """Google Cloud TTS provider."""

    def __init__(self, credentials_path: str, language_code: str = "en-US",
                 voice_name: str = "en-US-Neural2-D", speaking_rate: float = 1.0,
                 pitch: float = 0.0, audio_encoding: str = "MP3"):
        """Initialize Google TTS.

        Args:
            credentials_path: Path to Google credentials JSON
            language_code: Language code
            voice_name: Voice name
            speaking_rate: Speaking rate
            pitch: Pitch adjustment
            audio_encoding: Audio encoding format
        """
        try:
            from google.cloud import texttospeech
            import os

            # Set credentials
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

            self.client = texttospeech.TextToSpeechAsyncClient()
            self.language_code = language_code
            self.voice_name = voice_name
            self.speaking_rate = speaking_rate
            self.pitch = pitch

            # Set audio encoding
            if audio_encoding == "MP3":
                self.audio_encoding = texttospeech.AudioEncoding.MP3
            elif audio_encoding == "LINEAR16":
                self.audio_encoding = texttospeech.AudioEncoding.LINEAR16
            else:
                self.audio_encoding = texttospeech.AudioEncoding.MP3

            self.texttospeech = texttospeech

        except ImportError:
            raise ImportError("Please install google-cloud-texttospeech: pip install google-cloud-texttospeech")

    async def synthesize(self, text: str) -> bytes:
        """Synthesize text to audio.

        Args:
            text: Text to synthesize

        Returns:
            Audio data
        """
        synthesis_input = self.texttospeech.SynthesisInput(text=text)

        voice = self.texttospeech.VoiceSelectionParams(
            language_code=self.language_code,
            name=self.voice_name
        )

        audio_config = self.texttospeech.AudioConfig(
            audio_encoding=self.audio_encoding,
            speaking_rate=self.speaking_rate,
            pitch=self.pitch
        )

        response = await self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        return response.audio_content

    async def synthesize_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        """Synthesize text to audio stream.

        Args:
            text: Text to synthesize

        Yields:
            Audio chunks
        """
        # Google TTS doesn't natively support streaming, so we'll chunk the audio
        audio_data = await self.synthesize(text)

        # Send in chunks of 4KB
        chunk_size = 4096
        for i in range(0, len(audio_data), chunk_size):
            yield audio_data[i:i + chunk_size]


class TTSModule:
    """Main TTS module that manages different providers."""

    def __init__(self, config: dict):
        """Initialize TTS module.

        Args:
            config: TTS configuration dictionary
        """
        self.config = config
        self.provider = self._create_provider()

    def _create_provider(self) -> TTSProvider:
        """Create TTS provider based on configuration.

        Returns:
            TTS provider instance
        """
        provider_name = self.config.get("provider", "openai")

        if provider_name == "openai":
            openai_config = self.config.get("openai", {})
            return OpenAITTS(
                api_key=openai_config.get("api_key"),
                model=openai_config.get("model", "tts-1"),
                voice=openai_config.get("voice", "alloy"),
                speed=openai_config.get("speed", 1.0)
            )
        elif provider_name == "google":
            google_config = self.config.get("google", {})
            return GoogleTTS(
                credentials_path=google_config.get("credentials_path"),
                language_code=google_config.get("language_code", "en-US"),
                voice_name=google_config.get("voice_name", "en-US-Neural2-D"),
                speaking_rate=google_config.get("speaking_rate", 1.0),
                pitch=google_config.get("pitch", 0.0),
                audio_encoding=google_config.get("audio_encoding", "MP3")
            )
        else:
            raise ValueError(f"Unknown TTS provider: {provider_name}")

    async def synthesize(self, text: str) -> bytes:
        """Synthesize text to audio.

        Args:
            text: Text to synthesize

        Returns:
            Audio data
        """
        return await self.provider.synthesize(text)

    async def synthesize_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        """Synthesize text to audio stream.

        Args:
            text: Text to synthesize

        Yields:
            Audio chunks
        """
        async for chunk in self.provider.synthesize_stream(text):
            yield chunk
