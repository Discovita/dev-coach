"""
Segment-part generation.

Two steps so the admin UI gets immediate feedback:

1. ``create_pending_asset`` — synchronous, called from the request. Creates the
   next versioned MeditationAsset in QUEUED state (snapshotting the current
   prompt/script) so the QC screen sees a pending part the instant Generate is
   clicked and starts polling.
2. ``generate_asset`` — the Celery task body. Loads that asset, flips it to
   GENERATING, calls the media provider, uploads to S3, and promotes it to
   active (demoting the prior active in a transaction). On provider failure the
   asset is marked FAILED with an error code.
"""

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import Max

from apps.meditations.models import Meditation, MeditationAsset, MeditationSegment
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


def create_pending_asset(segment: MeditationSegment, kind: str) -> MeditationAsset:
    """
    Create a QUEUED asset for the next version of (segment, kind), snapshotting
    the current prompt/script. Returns it immediately so the UI can show and
    poll it. Marks the meditation as generating.
    """
    kind = MeditationAssetKind(kind)
    prompt_snapshot = (
        segment.current_video_prompt
        if kind == MeditationAssetKind.VIDEO
        else segment.current_audio_script
    )
    asset = MeditationAsset.objects.create(
        segment=segment,
        kind=kind,
        version=_next_version(segment, kind),
        prompt_snapshot=prompt_snapshot,
        status=MeditationAssetStatus.QUEUED,
    )
    Meditation.objects.filter(
        id=segment.meditation_id, status=MeditationStatus.PENDING
    ).update(status=MeditationStatus.GENERATING_PARTS)
    return asset


def generate_asset(asset_id: str) -> MeditationAsset:
    """
    Run generation for an existing QUEUED asset: provider → S3 → READY (active),
    or FAILED with an error code. Idempotent inputs come from the asset itself
    (its snapshotted prompt) and its segment's identity.
    """
    asset = MeditationAsset.objects.select_related(
        "segment__identity", "segment__meditation"
    ).get(id=asset_id)
    segment = asset.segment
    kind = MeditationAssetKind(asset.kind)

    asset.status = MeditationAssetStatus.GENERATING
    asset.save(update_fields=["status", "updated_at"])

    try:
        result = _run_provider(segment, kind, asset.prompt_snapshot)
        ext = _EXTENSIONS[kind]
        saved_key = default_storage.save(
            _asset_key(segment, kind, asset.version, ext), ContentFile(result.data)
        )
        with transaction.atomic():
            MeditationAsset.objects.filter(
                segment=segment, kind=kind, is_active=True
            ).exclude(pk=asset.pk).update(is_active=False)
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
        log.info(
            f"Generated {kind} v{asset.version} for segment {segment.id}: {saved_key}"
        )
    except MediaGenerationError as e:
        log.warning(f"Generation failed for asset {asset_id} ({kind}): {e}")
        asset.status = MeditationAssetStatus.FAILED
        asset.error_code = e.error_code
        asset.save(update_fields=["status", "error_code", "updated_at"])

    return asset


def _run_provider(segment: MeditationSegment, kind: str, prompt: str):
    """Call the right media provider with the snapshotted prompt/script."""
    if kind == MeditationAssetKind.VIDEO:
        first_frame = _read_identity_image(segment.identity)
        provider = MediaProviderFactory.create_video_provider()
        return provider.generate(prompt=prompt, first_frame=first_frame)

    provider = MediaProviderFactory.create_audio_provider()
    return provider.generate(script=prompt)


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
