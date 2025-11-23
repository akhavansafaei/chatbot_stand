"""ASR (Automatic Speech Recognition) module with local options."""

import io
import wave
import json
from typing import Optional, AsyncGenerator
from abc import ABC, abstractmethod


class ASRProvider(ABC):
    """Abstract base class for ASR providers."""

    @abstractmethod
    async def transcribe(self, audio_data: bytes) -> str:
        """Transcribe audio data to text.

        Args:
            audio_data: Audio data in bytes

        Returns:
            Transcribed text
        """
        pass

    @abstractmethod
    async def transcribe_stream(self, audio_chunk: bytes) -> AsyncGenerator[str, None]:
        """Transcribe audio stream in chunks.

        Args:
            audio_chunk: Audio chunk in bytes

        Yields:
            Partial transcriptions
        """
        pass


class WhisperASR(ASRProvider):
    """OpenAI Whisper ASR provider (local)."""

    def __init__(self, model: str = "base", language: str = "en", device: str = "cpu"):
        """Initialize Whisper ASR.

        Args:
            model: Whisper model size
            language: Language code
            device: Device to run on (cpu/cuda)
        """
        try:
            import whisper
            self.model = whisper.load_model(model, device=device)
            self.language = language
        except ImportError:
            raise ImportError("Please install openai-whisper: pip install openai-whisper")

    async def transcribe(self, audio_data: bytes) -> str:
        """Transcribe audio data to text.

        Args:
            audio_data: Audio data in WAV format

        Returns:
            Transcribed text
        """
        import tempfile
        import os

        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name

        try:
            result = self.model.transcribe(temp_path, language=self.language)
            return result["text"].strip()
        finally:
            os.unlink(temp_path)

    async def transcribe_stream(self, audio_chunk: bytes) -> AsyncGenerator[str, None]:
        """Transcribe audio stream (Whisper doesn't natively support streaming).

        Args:
            audio_chunk: Audio chunk in bytes

        Yields:
            Transcription when complete
        """
        # For Whisper, we'll transcribe the complete chunk
        text = await self.transcribe(audio_chunk)
        if text:
            yield text


class VoskASR(ASRProvider):
    """Vosk ASR provider (local)."""

    def __init__(self, model_path: str, sample_rate: int = 16000):
        """Initialize Vosk ASR.

        Args:
            model_path: Path to Vosk model
            sample_rate: Audio sample rate
        """
        try:
            from vosk import Model, KaldiRecognizer
            self.model = Model(model_path)
            self.sample_rate = sample_rate
            self.Model = Model
            self.KaldiRecognizer = KaldiRecognizer
        except ImportError:
            raise ImportError("Please install vosk: pip install vosk")

    async def transcribe(self, audio_data: bytes) -> str:
        """Transcribe audio data to text.

        Args:
            audio_data: Audio data in WAV format

        Returns:
            Transcribed text
        """
        recognizer = self.KaldiRecognizer(self.model, self.sample_rate)
        recognizer.AcceptWaveform(audio_data)
        result = json.loads(recognizer.FinalResult())
        return result.get("text", "").strip()

    async def transcribe_stream(self, audio_chunk: bytes) -> AsyncGenerator[str, None]:
        """Transcribe audio stream in real-time.

        Args:
            audio_chunk: Audio chunk in bytes

        Yields:
            Partial transcriptions
        """
        recognizer = self.KaldiRecognizer(self.model, self.sample_rate)

        if recognizer.AcceptWaveform(audio_chunk):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip()
            if text:
                yield text
        else:
            partial = json.loads(recognizer.PartialResult())
            text = partial.get("partial", "").strip()
            if text:
                yield text


class ASRModule:
    """Main ASR module that manages different providers."""

    def __init__(self, config: dict):
        """Initialize ASR module.

        Args:
            config: ASR configuration dictionary
        """
        self.config = config
        self.provider = self._create_provider()

    def _create_provider(self) -> ASRProvider:
        """Create ASR provider based on configuration.

        Returns:
            ASR provider instance
        """
        provider_name = self.config.get("provider", "whisper_local")

        if provider_name == "whisper_local":
            whisper_config = self.config.get("whisper", {})
            return WhisperASR(
                model=whisper_config.get("model", "base"),
                language=whisper_config.get("language", "en"),
                device=whisper_config.get("device", "cpu")
            )
        elif provider_name == "vosk_local":
            vosk_config = self.config.get("vosk", {})
            return VoskASR(
                model_path=vosk_config.get("model_path"),
                sample_rate=vosk_config.get("sample_rate", 16000)
            )
        else:
            raise ValueError(f"Unknown ASR provider: {provider_name}")

    async def transcribe(self, audio_data: bytes) -> str:
        """Transcribe audio data.

        Args:
            audio_data: Audio data in bytes

        Returns:
            Transcribed text
        """
        return await self.provider.transcribe(audio_data)

    async def transcribe_stream(self, audio_chunk: bytes) -> AsyncGenerator[str, None]:
        """Transcribe audio stream.

        Args:
            audio_chunk: Audio chunk in bytes

        Yields:
            Partial transcriptions
        """
        async for text in self.provider.transcribe_stream(audio_chunk):
            yield text
