from django.db import models


class VideoProvider(models.TextChoices):
    """
    Enum of supported video-generation providers for meditations.

    Used to select which concrete video provider the media factory builds.
    As new providers are added, add them here and wire a branch into
    ``MediaProviderFactory.create_video_provider``.
    """

    GOOGLE_VEO = "GOOGLE_VEO", "Google Veo"

    @classmethod
    def from_string(cls, provider_name: str) -> "VideoProvider":
        """Convert a string representation to a VideoProvider enum value."""
        name_map = {
            "google_veo": cls.GOOGLE_VEO,
            "veo": cls.GOOGLE_VEO,
            "google": cls.GOOGLE_VEO,
        }
        normalized = provider_name.strip().lower()
        if normalized not in name_map:
            raise ValueError(f"Unknown video provider: {provider_name}")
        return name_map[normalized]


class AudioProvider(models.TextChoices):
    """
    Enum of supported audio-generation (text-to-speech) providers for
    meditations.

    Used to select which concrete audio provider the media factory builds.
    """

    GEMINI_TTS = "GEMINI_TTS", "Google Gemini TTS"

    @classmethod
    def from_string(cls, provider_name: str) -> "AudioProvider":
        """Convert a string representation to an AudioProvider enum value."""
        name_map = {
            "gemini_tts": cls.GEMINI_TTS,
            "gemini": cls.GEMINI_TTS,
            "google": cls.GEMINI_TTS,
            "tts": cls.GEMINI_TTS,
        }
        normalized = provider_name.strip().lower()
        if normalized not in name_map:
            raise ValueError(f"Unknown audio provider: {provider_name}")
        return name_map[normalized]
