import uuid

from django.db import models

from apps.identities.models import Identity
from apps.meditations.models.meditation import Meditation


class MeditationSegment(models.Model):
    """
    One identity's section within a meditation. Holds the current editable
    prompt/script that seeds the next generation of its video and audio parts;
    the generated parts themselves are versioned MeditationAsset rows.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meditation = models.ForeignKey(
        Meditation,
        on_delete=models.CASCADE,
        related_name="segments",
    )
    identity = models.ForeignKey(
        Identity,
        on_delete=models.CASCADE,
        related_name="meditation_segments",
        help_text="The identity this segment is built from",
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order within the meditation (mirrors identity order)",
    )
    current_video_prompt = models.TextField(
        blank=True,
        default="",
        help_text="Editable prompt that seeds the next video generation",
    )
    current_audio_script = models.TextField(
        blank=True,
        default="",
        help_text="Editable narration script that seeds the next audio generation",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["meditation", "identity"],
                name="unique_meditation_identity_segment",
            )
        ]

    def __str__(self):
        return f"Segment {self.order} ({self.identity_id}) of {self.meditation_id}"
