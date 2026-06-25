"""
Media Generation Base Module

Defines the contracts the meditations feature uses to generate media, plus the
standard result/error types. Callers (orchestration, Celery tasks) interact
exclusively with these interfaces; the concrete provider is resolved by
``MediaProviderFactory`` and is an implementation detail.

Two capability families:
    BaseVideoProvider  — image-to-video (first frame -> short clip)
    BaseAudioProvider  — text-to-speech (script -> narration)

Concrete implementations live alongside this module:
    VeoVideoProvider     (services/media/veo_video_provider.py)
    GeminiTTSProvider    (services/media/gemini_tts_provider.py)

To add a new provider, create a class inheriting the relevant base, implement
its abstract methods, register it in the factory, and add a value to the
matching enum in ``enums/media.py``.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from enums.media import AudioProvider, VideoProvider


@dataclass
class MediaResult:
    """
    Standard output of any media provider.

    ``data`` is the raw bytes ready to upload to S3; the remaining fields are
    metadata callers persist alongside the asset. Dimensions are video-only and
    left ``None`` for audio.
    """

    data: bytes
    mime_type: str
    provider: str
    model: str
    duration_seconds: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    extra: dict = field(default_factory=dict)


class MediaGenerationError(Exception):
    """
    Custom exception for media generation failures with a machine-readable
    error code, mirroring ``ImageGenerationError`` so callers can surface a
    consistent retry UX across image, video, and audio generation.
    """

    BLOCKED_PROMPT = "BLOCKED_PROMPT"
    SAFETY_BLOCK = "SAFETY_BLOCK"
    RATE_LIMITED = "RATE_LIMITED"
    MODEL_OVERLOADED = "MODEL_OVERLOADED"
    TIMEOUT = "TIMEOUT"
    EMPTY_RESPONSE = "EMPTY_RESPONSE"
    UNKNOWN = "UNKNOWN"

    def __init__(
        self, message: str, error_code: str = "UNKNOWN", details: Optional[str] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)

    def to_dict(self) -> dict:
        return {
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
        }

    @classmethod
    def from_exception(cls, e: Exception) -> "MediaGenerationError":
        """
        Convert a generic provider/SDK exception into a MediaGenerationError,
        parsing common error patterns for a specific error code.
        """
        if isinstance(e, cls):
            return e

        error_str = str(e).lower()

        if "503" in str(e) or "unavailable" in error_str or "overloaded" in error_str:
            return cls(
                message="The media model is currently overloaded. Please wait a moment and try again.",
                error_code=cls.MODEL_OVERLOADED,
                details=str(e),
            )

        if "429" in str(e) or "rate limit" in error_str or "quota" in error_str:
            return cls(
                message="Too many requests. Please wait a moment before trying again.",
                error_code=cls.RATE_LIMITED,
                details=str(e),
            )

        if "safety" in error_str or "blocked" in error_str:
            return cls(
                message="The request was blocked by safety filters. Please modify the prompt and try again.",
                error_code=cls.SAFETY_BLOCK,
                details=str(e),
            )

        return cls(
            message=f"Media generation failed: {str(e)}",
            error_code=cls.UNKNOWN,
            details=str(e),
        )


class BaseVideoProvider(ABC):
    """Contract for image-to-video providers."""

    @abstractmethod
    def generate(
        self,
        *,
        prompt: str,
        first_frame: bytes,
        first_frame_mime: str = "image/png",
        aspect_ratio: str = "16:9",
        resolution: str = "1080p",
        duration_seconds: int = 8,
    ) -> MediaResult:
        """
        Generate a short video clip from a text prompt and a first-frame image.

        Returns a MediaResult with the encoded video bytes and metadata.
        Raises MediaGenerationError on failure.
        """

    @abstractmethod
    def provider_name(self) -> VideoProvider:
        """Return the VideoProvider enum value for this implementation."""


class BaseAudioProvider(ABC):
    """Contract for text-to-speech providers."""

    @abstractmethod
    def generate(self, *, script: str, voice: Optional[str] = None) -> MediaResult:
        """
        Generate narration audio from a text script.

        Returns a MediaResult with the encoded audio bytes and metadata.
        Raises MediaGenerationError on failure.
        """

    @abstractmethod
    def provider_name(self) -> AudioProvider:
        """Return the AudioProvider enum value for this implementation."""
