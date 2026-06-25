"""
generate_segment_part — generate one video or audio part for a segment.

Creates a new versioned MeditationAsset, calls the appropriate media provider,
uploads the result to S3, and promotes the new asset to active (demoting the
prior active in a transaction). On provider failure the asset is marked FAILED
with an error code. This is the synchronous core; the Celery task wraps it.
"""

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import Max

from apps.meditations.models import (
    Meditation,
    MeditationAsset,
    MeditationSegment,
)
from enums.meditation import (
    MeditationAssetKind,
    MeditationAssetStatus,
    MeditationStatus,
)
from services.logger import configure_logging
from services.media import MediaGenerationError, MediaProviderFactory

log = configure_logging(__name__, log_level="INFO")

_EXTENSIONS = {
    MeditationAssetKind.VIDEO: "mp4",
    MeditationAssetKind.AUDIO: "wav",
}


def _next_version(segment: MeditationSegment, kind: str) -> int:
    current_max = MeditationAsset.objects.filter(segment=segment, kind=kind).aggregate(
        Max("version")
    )["version__max"]
    return (current_max or 0) + 1


def _asset_key(segment: MeditationSegment, kind: str, version: int, ext: str) -> str:
    return (
        f"meditations/{segment.meditation_id}/{segment.id}/"
        f"{kind.lower()}_v{version}.{ext}"
    )


def generate_segment_part(segment_id: str, kind: str) -> MeditationAsset:
    """
    Generate one part (``kind`` = VIDEO or AUDIO) for the given segment.

    Returns the created MeditationAsset (READY on success, FAILED on a provider
    error). Raises ValueError for an unknown kind or missing inputs.
    """
    kind = MeditationAssetKind(kind)
    segment = MeditationSegment.objects.select_related("identity", "meditation").get(
        id=segment_id
    )

    if kind == MeditationAssetKind.VIDEO:
        prompt_snapshot = segment.current_video_prompt
    else:
        prompt_snapshot = segment.current_audio_script

    version = _next_version(segment, kind)
    asset = MeditationAsset.objects.create(
        segment=segment,
        kind=kind,
        version=version,
        prompt_snapshot=prompt_snapshot,
        status=MeditationAssetStatus.GENERATING,
    )

    # Mark the meditation as actively generating parts.
    Meditation.objects.filter(
        id=segment.meditation_id, status=MeditationStatus.PENDING
    ).update(status=MeditationStatus.GENERATING_PARTS)

    try:
        result = _run_provider(segment, kind)
        ext = _EXTENSIONS[kind]
        saved_key = default_storage.save(
            _asset_key(segment, kind, version, ext), ContentFile(result.data)
        )
        with transaction.atomic():
            MeditationAsset.objects.filter(
                segment=segment, kind=kind, is_active=True
            ).update(is_active=False)
            asset.s3_key = saved_key
            asset.status = MeditationAssetStatus.READY
            asset.is_active = True
            asset.error_code = ""
            asset.save(
                update_fields=[
                    "s3_key",
                    "status",
                    "is_active",
                    "error_code",
                    "updated_at",
                ]
            )
        log.info(f"Generated {kind} v{version} for segment {segment_id}: {saved_key}")
    except MediaGenerationError as e:
        log.warning(f"Generation failed for segment {segment_id} ({kind}): {e}")
        asset.status = MeditationAssetStatus.FAILED
        asset.error_code = e.error_code
        asset.save(update_fields=["status", "error_code", "updated_at"])

    return asset


def _run_provider(segment: MeditationSegment, kind: str):
    """Call the right media provider and return its MediaResult."""
    if kind == MeditationAssetKind.VIDEO:
        first_frame = _read_identity_image(segment.identity)
        provider = MediaProviderFactory.create_video_provider()
        return provider.generate(
            prompt=segment.current_video_prompt, first_frame=first_frame
        )

    provider = MediaProviderFactory.create_audio_provider()
    return provider.generate(script=segment.current_audio_script)


def _read_identity_image(identity) -> bytes:
    if not identity.image:
        raise MediaGenerationError(
            "Identity has no image to use as the first frame.",
            MediaGenerationError.EMPTY_RESPONSE,
        )
    identity.image.open("rb")
    try:
        return identity.image.read()
    finally:
        identity.image.close()
