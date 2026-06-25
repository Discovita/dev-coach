"""
Celery task that runs generation for a pending meditation asset.

The asset is created (QUEUED) synchronously in the request so the UI sees it
immediately; this task fills it in. Generation is slow (Veo is a long-poll,
~minutes); runs serialized on the existing worker.
"""

from celery import shared_task

from apps.meditations.services import generate_asset


@shared_task
def generate_segment_part_task(asset_id: str) -> None:
    """Generate the media for a pending MeditationAsset asynchronously."""
    generate_asset(asset_id)
