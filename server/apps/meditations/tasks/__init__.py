"""
Meditation Celery tasks.
"""

from apps.meditations.tasks.generate_segment_part import generate_segment_part_task

__all__ = ["generate_segment_part_task"]
