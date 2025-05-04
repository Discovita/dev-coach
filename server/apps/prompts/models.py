import uuid
from django.db import models

from django.db.models import JSONField
from enums.coaching_state import CoachingState
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
    coach_state = models.CharField(
        max_length=32,
        choices=CoachingState.choices,
        help_text="The state of the coach this prompt is associated with.",
    )
    version = models.IntegerField(default=1, help_text="Version number of the prompt")
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    body = models.TextField(help_text="Prompt body")
    required_context_keys = JSONField(
        models.CharField(max_length=64, choices=ContextKey.choices),
        default=list,
        help_text="List of required context keys for this prompt",
    )
    allowed_action_types = JSONField(
        models.CharField(max_length=64, choices=ActionType.choices),
        default=list,
        help_text="List of allowed action types for this prompt",
    )
    is_active = models.BooleanField(default=True, help_text="Is this prompt active?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("coach_state", "version")
