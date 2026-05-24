"""
Break model — backend-tracked, soft-blocking pause between coaching sessions.

A `Break` row opens when the user acknowledges a session outro video and
clicks Continue (the `START_BREAK(session_key)` action). It closes when
the user clicks "I'm Ready" on the break card (the `END_BREAK()` action),
which stamps `ended_at`.

State is exposed to the frontend as `on_break: bool`, derived from
`Break.objects.filter(user=u, ended_at__isnull=True).exists()`.

Note: the on-disk filename is `break_model.py` rather than `break.py`
because `break` is a reserved word in Python — `from … .break import …`
is a syntax error. Callers should import via the package re-export:
`from apps.coach_states.models import Break`.
"""

import uuid

from django.db import models

from apps.chat_messages.models import ChatMessage
from apps.users.models import User


class Break(models.Model):
    """
    A single pause between coaching sessions for one user.

    At most one row per user may have `ended_at IS NULL` at any time — the
    PR 7 `START_BREAK` handler enforces this with a `ValidationError`.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique identifier for this break.",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="breaks",
        help_text="The user this break belongs to.",
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the break opened (set on creation).",
    )
    ended_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            "Timestamp when the user clicked 'I'm Ready' to end the break. "
            "NULL means the user is still on a break."
        ),
    )
    triggered_by_session = models.CharField(
        max_length=255,
        help_text=(
            "Session key the user just finished when the break started "
            "(e.g., 'brainstorming_session')."
        ),
    )
    coach_message = models.ForeignKey(
        ChatMessage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="break_anchors",
        help_text=(
            "The coach ChatMessage carrying the SESSION_BREAK component "
            "that opened this break. Nullable so a break survives chat "
            "message deletion."
        ),
    )

    class Meta:
        ordering = ("-started_at",)

    def __str__(self) -> str:
        state = "open" if self.ended_at is None else "closed"
        return (
            f"Break for {self.user.email} "
            f"({self.triggered_by_session}, {state})"
        )
