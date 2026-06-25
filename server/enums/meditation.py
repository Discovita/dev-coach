from django.db import models


class MeditationStatus(models.TextChoices):
    """Lifecycle status of a Meditation."""

    PENDING = "PENDING", "Pending"
    GENERATING_PARTS = "GENERATING_PARTS", "Generating parts"
    READY_FOR_QC = "READY_FOR_QC", "Ready for QC"
    ASSEMBLING = "ASSEMBLING", "Assembling"
    COMPLETE = "COMPLETE", "Complete"
    FAILED = "FAILED", "Failed"


class MeditationAssetKind(models.TextChoices):
    """Which part of a segment an asset is."""

    VIDEO = "VIDEO", "Video"
    AUDIO = "AUDIO", "Audio"


class MeditationAssetStatus(models.TextChoices):
    """Generation status of a single asset version."""

    QUEUED = "QUEUED", "Queued"
    GENERATING = "GENERATING", "Generating"
    READY = "READY", "Ready"
    FAILED = "FAILED", "Failed"
