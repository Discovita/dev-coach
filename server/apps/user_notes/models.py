import uuid
from django.db import models
from apps.users.models import User
from apps.chat_messages.models import ChatMessage

class UserNote(models.Model):
    """
    Stores a single note about a user, extracted by the Sentinel agent.
    Each note is associated with a user and may reference the chat message that prompted its creation.
    Used by the Sentinel User Notes system to provide long-term memory for the coach.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique identifier for this user note."
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_notes",
        help_text="The user this note belongs to."
    )
    note = models.TextField(
        help_text="A note about the user, extracted from chat."
    )
    source_message = models.ForeignKey(
        ChatMessage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="The chat message that prompted this note, if applicable."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this note was created."
    )

    def __str__(self):
        return f"Note for {self.user.email}: {self.note[:40]}..."
