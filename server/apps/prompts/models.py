import uuid
from django.db import models

from django.contrib.postgres.fields import ArrayField
from server.enums.coaching_phase import CoachingPhase
from enums.context_keys import ContextKey
from enums.action_type import ActionType


class Prompt(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique identifier for this object.",
    )
    coaching_phase = models.CharField(
        max_length=32,
        choices=CoachingPhase.choices,
        help_text="The phase of the coach this prompt is associated with.",
    )
    version = models.IntegerField(default=1, help_text="Version number of the prompt")
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    body = models.TextField(help_text="Prompt body")
    required_context_keys = ArrayField(
        models.CharField(max_length=64, choices=ContextKey.choices),
        default=list,
        blank=True,
        help_text="List of required context keys for this prompt.",
    )
    allowed_actions = ArrayField(
        models.CharField(max_length=64, choices=ActionType.choices),
        default=list,
        blank=True,
        help_text="List of allowed action types for this prompt.",
    )
    is_active = models.BooleanField(default=True, help_text="Is this prompt active?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("coaching_phase", "version")
