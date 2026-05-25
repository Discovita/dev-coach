"""
Action model

Records each coach-triggered action for a user, linked to the coach message
that caused it.

See: docs/docs/core-systems/action-handler/overview.md (Procedures / Dev Coach).
"""

import uuid

from django.db import models

from apps.chat_messages.models import ChatMessage
from apps.users.models import User
from enums.action_type import ActionType


class Action(models.Model):
    """
    Tracks actions taken by the coach during conversations.
    Each action is linked to the specific coach message that triggered it.

    Related to:
    - apps.users.models.User (FK via user)
    - apps.chat_messages.models.ChatMessage (FK via coach_message)
    - apps.test_scenario.models.TestScenario (optional FK via test_scenario)
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique identifier for this action.",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="actions",
        help_text="The user this action belongs to.",
        db_index=True,
    )

    action_type = models.CharField(
        max_length=64,
        choices=ActionType.choices,
        help_text="Type of action performed by the coach.",
    )

    parameters = models.JSONField(
        help_text="Parameters passed to the action (stored as JSON).",
    )

    result_summary = models.TextField(
        null=True,
        blank=True,
        help_text="Natural language description of what the action accomplished.",
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the action was first recorded.",
        db_index=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this row was last updated (e.g. summary tweaks).",
        db_index=True,
    )

    coach_message = models.ForeignKey(
        ChatMessage,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="triggered_actions",
        help_text=(
            "ChatMessage that triggered this action. Typically the coach "
            "message for LLM-emitted actions, or the user message for "
            "user-button-driven actions. Nullable for programmatic-only "
            "turns (`message=None` in `process_message`, e.g. the video "
            "Continue button) where no triggering ChatMessage exists."
        ),
    )

    test_scenario = models.ForeignKey(
        "test_scenario.TestScenario",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text=(
            "Test scenario this action is associated with (for test data isolation)."
        ),
    )

    class Meta:
        verbose_name = "Action"
        verbose_name_plural = "Actions"
        ordering = ["timestamp"]
        indexes = [
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["coach_message"]),
            models.Index(fields=["action_type"]),
        ]

    def __str__(self) -> str:
        return f"{self.action_type} - {self.user.email} - {self.timestamp}"
