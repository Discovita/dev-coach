"""
Veo video provider.

Concrete BaseVideoProvider backed by Google's Veo models via the google-genai
SDK, reusing the same ``GEMINI_API_KEY`` as the identity image service. This is
a "dumb" provider: it takes a prompt + first-frame image and returns encoded
video bytes. Prompt construction and persistence belong to callers.

Verified facts (see the meditations braindump's "Veo spike findings"):
  - Veo generation is a long-running async operation: submit -> poll
    ``operations.get`` until ``done`` -> download.
  - Default model ``veo-3.1-fast-generate-preview`` (3.0/2.0 are deprecated).
  - 1080p / 4k force an 8s duration; 720p allows 4/6/8s. Output is H.264 + AAC
    mp4 at 24fps; Veo's always-on audio track is ignored by callers.
  - Image-to-video of a person requires ``person_generation="allow_adult"``.
"""

import os
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types

from enums.media import VideoProvider
from services.logger import configure_logging
from services.media.base import BaseVideoProvider, MediaGenerationError, MediaResult

# Load .env so the provider works in standalone scripts; in the running app
# Django has already populated the environment.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

log = configure_logging(__name__, log_level="INFO")

# Pixel dimensions per resolution label, used to stamp asset metadata.
RESOLUTION_DIMENSIONS = {
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "4k": (3840, 2160),
}


class VeoVideoProvider(BaseVideoProvider):
    """Generate short video clips with Google Veo (image-to-video)."""

    DEFAULT_MODEL = "veo-3.1-fast-generate-preview"
    PERSON_GENERATION = "allow_adult"
    POLL_INTERVAL_SECONDS = 10
    TIMEOUT_SECONDS = 600

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        *,
        poll_interval: Optional[int] = None,
        timeout: Optional[int] = None,
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is required. Set it in .env or pass to constructor."
            )
        self.model = model or os.getenv("MEDITATIONS_VEO_MODEL") or self.DEFAULT_MODEL
        self.poll_interval = (
            poll_interval if poll_interval is not None else self.POLL_INTERVAL_SECONDS
        )
        self.timeout = timeout if timeout is not None else self.TIMEOUT_SECONDS
        self.client = genai.Client(api_key=self.api_key)
        log.info(f"VeoVideoProvider initialized (model={self.model})")

    def provider_name(self) -> VideoProvider:
        return VideoProvider.GOOGLE_VEO

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
        # 1080p and 4k only support an 8s duration; coerce and warn rather than
        # let the API reject the request.
        if resolution.lower() != "720p" and duration_seconds != 8:
            log.warning(
                f"Veo {resolution} only supports 8s; overriding "
                f"duration_seconds={duration_seconds} -> 8"
            )
            duration_seconds = 8

        config = types.GenerateVideosConfig(
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            number_of_videos=1,
            person_generation=self.PERSON_GENERATION,
            duration_seconds=duration_seconds,
        )

        log.info(
            f"Generating video: model={self.model}, resolution={resolution}, "
            f"aspect_ratio={aspect_ratio}, duration={duration_seconds}s"
        )

        try:
            operation = self.client.models.generate_videos(
                model=self.model,
                prompt=prompt,
                image=types.Image(image_bytes=first_frame, mime_type=first_frame_mime),
                config=config,
            )
        except Exception as e:
            log.error(f"Veo submit failed: {e}", exc_info=True)
            raise MediaGenerationError.from_exception(e)

        operation = self._poll(operation)

        if operation.error:
            raise MediaGenerationError(
                message="Veo reported an error while generating the video.",
                error_code=MediaGenerationError.UNKNOWN,
                details=str(operation.error),
            )

        videos = (
            getattr(operation.response, "generated_videos", None)
            if operation.response
            else None
        ) or []
        if not videos:
            raise MediaGenerationError(
                "Veo returned no video.", MediaGenerationError.EMPTY_RESPONSE
            )

        video = videos[0].video
        try:
            self.client.files.download(file=video)
        except Exception as e:
            log.error(f"Veo download failed: {e}", exc_info=True)
            raise MediaGenerationError.from_exception(e)

        data = getattr(video, "video_bytes", None)
        if not data:
            raise MediaGenerationError(
                "Veo video contained no bytes.", MediaGenerationError.EMPTY_RESPONSE
            )

        width, height = RESOLUTION_DIMENSIONS.get(resolution.lower(), (None, None))
        log.info(f"Veo video generated: {len(data)} bytes")
        return MediaResult(
            data=data,
            mime_type=getattr(video, "mime_type", None) or "video/mp4",
            provider=VideoProvider.GOOGLE_VEO.value,
            model=self.model,
            duration_seconds=float(duration_seconds),
            width=width,
            height=height,
        )

    def _poll(self, operation):
        """Poll the long-running operation until done or timed out."""
        elapsed = 0
        while not operation.done:
            if elapsed >= self.timeout:
                raise MediaGenerationError(
                    f"Veo generation timed out after {self.timeout}s.",
                    MediaGenerationError.TIMEOUT,
                )
            time.sleep(self.poll_interval)
            elapsed += self.poll_interval
            operation = self.client.operations.get(operation)
        return operation
