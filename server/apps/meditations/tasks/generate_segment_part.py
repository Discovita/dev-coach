"""
Celery task wrapping the segment-part generation service.

Generation is slow (Veo is a long-poll, ~minutes) so the admin enqueues it and
polls asset status. Runs serialized on the existing worker.
"""

from celery import shared_task

from apps.meditations.services import generate_segment_part


@shared_task
def generate_segment_part_task(segment_id: str, kind: str) -> None:
    """Generate one part (VIDEO or AUDIO) for *segment_id* asynchronously."""
    generate_segment_part(segment_id, kind)
