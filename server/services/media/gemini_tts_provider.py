"""
Gemini TTS audio provider.

Concrete BaseAudioProvider backed by Google's Gemini text-to-speech models via
the google-genai SDK, reusing the same ``GEMINI_API_KEY`` as the rest of the
Google integration. It narrates a script (the identity's "I Am" statement, or
an admin-edited version) in a single fixed brand voice.

Gemini TTS returns raw 24kHz, 16-bit, mono PCM; this provider wraps it in a WAV
container so callers get a self-describing, playable file to store in S3.
"""

import io
import os
import wave
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types

from enums.media import AudioProvider
from services.logger import configure_logging
from services.media.base import BaseAudioProvider, MediaGenerationError, MediaResult

# Load .env so the provider works in standalone scripts; in the running app
# Django has already populated the environment.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

log = configure_logging(__name__, log_level="INFO")


class GeminiTTSProvider(BaseAudioProvider):
    """Generate narration audio with Google Gemini TTS."""

    DEFAULT_MODEL = "gemini-2.5-flash-preview-tts"
    DEFAULT_VOICE = "Kore"

    # Gemini TTS PCM characteristics (24kHz, 16-bit, mono).
    SAMPLE_RATE = 24000
    SAMPLE_WIDTH = 2
    CHANNELS = 1

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        voice: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is required. Set it in .env or pass to constructor."
            )
        self.model = model or os.getenv("MEDITATIONS_TTS_MODEL") or self.DEFAULT_MODEL
        self.voice = voice or os.getenv("MEDITATIONS_TTS_VOICE") or self.DEFAULT_VOICE
        self.client = genai.Client(api_key=self.api_key)
        log.info(
            f"GeminiTTSProvider initialized (model={self.model}, voice={self.voice})"
        )

    def provider_name(self) -> AudioProvider:
        return AudioProvider.GEMINI_TTS

    def generate(self, *, script: str, voice: Optional[str] = None) -> MediaResult:
        voice_name = voice or self.voice
        config = types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice_name
                    )
                )
            ),
        )

        log.info(f"Generating TTS audio: model={self.model}, voice={voice_name}")

        try:
            response = self.client.models.generate_content(
                model=self.model, contents=script, config=config
            )
        except Exception as e:
            log.error(f"Gemini TTS failed: {e}", exc_info=True)
            raise MediaGenerationError.from_exception(e)

        pcm = self._extract_pcm(response)
        wav_bytes = self._pcm_to_wav(pcm)
        duration = len(pcm) / float(
            self.SAMPLE_RATE * self.SAMPLE_WIDTH * self.CHANNELS
        )

        log.info(f"TTS audio generated: {len(wav_bytes)} bytes, {duration:.2f}s")
        return MediaResult(
            data=wav_bytes,
            mime_type="audio/wav",
            provider=AudioProvider.GEMINI_TTS.value,
            model=self.model,
            duration_seconds=round(duration, 3),
        )

    def _extract_pcm(self, response) -> bytes:
        """Pull the raw PCM bytes out of a Gemini TTS response."""
        candidates = getattr(response, "candidates", None) or []
        for candidate in candidates:
            content = getattr(candidate, "content", None)
            parts = getattr(content, "parts", None) if content else None
            for part in parts or []:
                inline = getattr(part, "inline_data", None)
                data = getattr(inline, "data", None) if inline else None
                if data:
                    return data
        raise MediaGenerationError(
            "Gemini TTS returned no audio.", MediaGenerationError.EMPTY_RESPONSE
        )

    def _pcm_to_wav(self, pcm: bytes) -> bytes:
        """Wrap raw PCM in a WAV container."""
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(self.CHANNELS)
            wav_file.setsampwidth(self.SAMPLE_WIDTH)
            wav_file.setframerate(self.SAMPLE_RATE)
            wav_file.writeframes(pcm)
        return buffer.getvalue()
