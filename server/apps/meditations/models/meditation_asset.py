import uuid

from django.db import models

from apps.meditations.models.meditation_segment import MeditationSegment
from enums.meditation import MeditationAssetKind, MeditationAssetStatus


class MeditationAsset(models.Model):
    """
    A single generated video or audio part for a segment, versioned so the QC
    screen can compare old vs new and pick the active one. Each version
    snapshots the prompt/script that produced it for provenance.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    segment = models.ForeignKey(
        MeditationSegment,
        on_delete=models.CASCADE,
        related_name="assets",
    )
    kind = models.CharField(max_length=16, choices=MeditationAssetKind.choices)
    version = models.PositiveIntegerField(default=1)
    s3_key = models.CharField(
        max_length=1024,
        blank=True,
        default="",
        help_text="S3 key of the generated file (empty until generation completes)",
    )
    prompt_snapshot = models.TextField(
        blank=True,
        default="",
        help_text="The exact prompt/script that produced this version",
    )
    status = models.CharField(
        max_length=16,
        choices=MeditationAssetStatus.choices,
        default=MeditationAssetStatus.QUEUED,
    )
    error_code = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text="Machine-readable error code if generation failed",
    )
    is_active = models.BooleanField(
        default=False,
        help_text="The chosen version for this (segment, kind)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["kind", "version"]
        constraints = [
            models.UniqueConstraint(
                fields=["segment", "kind", "version"],
                name="unique_segment_kind_version",
            ),
            # At most one active asset per (segment, kind). Promotion of a new
            # version must demote the prior active one in the same transaction.
            models.UniqueConstraint(
                fields=["segment", "kind"],
                condition=models.Q(is_active=True),
                name="unique_active_asset_per_segment_kind",
            ),
        ]

    def __str__(self):
        return (
            f"{self.kind} v{self.version} ({self.status}) for segment {self.segment_id}"
        )
