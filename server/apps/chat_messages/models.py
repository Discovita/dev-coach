from django.db import models
from enums.message_role import MessageRole
from apps.users.models import User
import uuid


class ChatMessage(models.Model):
    """
    Stores a single message in the conversation history for the coaching chatbot.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="messages",
        help_text="The user this message belongs to.",
        db_index=True,
    )
    role = models.CharField(
        max_length=32,
        choices=MessageRole.choices,
        help_text="Role of the message sender (user or coach).",
    )
    content = models.TextField(help_text="Content of the message.")
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the message was sent.",
        db_index=True,
    )

    def __str__(self):
        return f"{self.role} ({self.user.email}): {self.content[:30]}"
