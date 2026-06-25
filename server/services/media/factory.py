"""
Media Provider Factory

Single entry point for creating media provider instances. Resolves the correct
concrete implementation for video and audio generation based on an explicit
provider, an environment override, or the default.

To add a new provider:
  1. Create a class in services/media/ that inherits BaseVideoProvider or
     BaseAudioProvider.
  2. Add a value to the matching enum in enums/media.py.
  3. Add the provider's branch below.

Environment overrides:
  MEDITATIONS_VIDEO_PROVIDER  (default: GOOGLE_VEO)
  MEDITATIONS_AUDIO_PROVIDER  (default: GEMINI_TTS)
"""

import os
from pathlib import Path
from typing import Optional, Union

from dotenv import load_dotenv

from enums.media import AudioProvider, VideoProvider
from services.logger import configure_logging
from services.media.base import BaseAudioProvider, BaseVideoProvider
from services.media.gemini_tts_provider import GeminiTTSProvider
from services.media.veo_video_provider import VeoVideoProvider

# Load .env so the factory works in standalone scripts; in the running app
# Django has already populated the environment.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

log = configure_logging(__name__, log_level="INFO")


class MediaProviderFactory:
    """Factory for creating media provider instances."""

    @staticmethod
    def create_video_provider(
        provider: Optional[Union[VideoProvider, str]] = None, **kwargs
    ) -> BaseVideoProvider:
        """
        Return a concrete BaseVideoProvider. Extra kwargs are forwarded to the
        provider constructor (e.g. api_key, model).
        """
        resolved = _resolve(
            provider,
            VideoProvider,
            env_var="MEDITATIONS_VIDEO_PROVIDER",
            default=VideoProvider.GOOGLE_VEO,
        )
        log.debug(f"Creating video provider: {resolved}")

        if resolved == VideoProvider.GOOGLE_VEO:
            return VeoVideoProvider(**kwargs)

        raise NotImplementedError(f"Video provider not implemented: {resolved}")

    @staticmethod
    def create_audio_provider(
        provider: Optional[Union[AudioProvider, str]] = None, **kwargs
    ) -> BaseAudioProvider:
        """
        Return a concrete BaseAudioProvider. Extra kwargs are forwarded to the
        provider constructor (e.g. api_key, model, voice).
        """
        resolved = _resolve(
            provider,
            AudioProvider,
            env_var="MEDITATIONS_AUDIO_PROVIDER",
            default=AudioProvider.GEMINI_TTS,
        )
        log.debug(f"Creating audio provider: {resolved}")

        if resolved == AudioProvider.GEMINI_TTS:
            return GeminiTTSProvider(**kwargs)

        raise NotImplementedError(f"Audio provider not implemented: {resolved}")


def _resolve(provider, enum_cls, *, env_var: str, default):
    """
    Resolve a provider selection from an explicit value, an env override, or
    the default. Accepts the enum, a string, or None.
    """
    if provider is None:
        provider = os.getenv(env_var)
    if provider is None:
        return default
    if isinstance(provider, enum_cls):
        return provider
    return enum_cls.from_string(str(provider))
