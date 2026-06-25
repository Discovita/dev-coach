"""
Media generation layer for the meditations feature.

Provider-agnostic interfaces for generating video and audio, with concrete
implementations resolved by ``MediaProviderFactory``. Callers depend only on
the base interfaces + the standard ``MediaResult`` / ``MediaGenerationError``
types, never on a concrete vendor.
"""

from services.media.base import (
    BaseAudioProvider,
    BaseVideoProvider,
    MediaGenerationError,
    MediaResult,
)
from services.media.factory import MediaProviderFactory
from services.media.gemini_tts_provider import GeminiTTSProvider
from services.media.veo_video_provider import VeoVideoProvider

__all__ = [
    "BaseAudioProvider",
    "BaseVideoProvider",
    "MediaGenerationError",
    "MediaResult",
    "MediaProviderFactory",
    "GeminiTTSProvider",
    "VeoVideoProvider",
]
