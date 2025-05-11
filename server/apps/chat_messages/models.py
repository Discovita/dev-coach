from django.db import models
from enums.message_role import MessageRole
from apps.users.models import User
import uuid


# TODO: add some flag to keep track of what coach state this message belongs to and what version of
# the prompt was used
# TODO: keep track of which coaching state the user was in when this message was sent.
class ChatMessage(models.Model):
    """
    Stores a single message in the conversation history for the coaching chatbot.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique identifier for this object.",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_messages",
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

    # NOTE: This is used when formatting the messages for prompts.
    def __str__(self):
        return f"{self.role}:\n{self.content}"
