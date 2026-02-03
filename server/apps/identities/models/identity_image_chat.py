"""
IdentityImageChat Model

Persists Gemini chat state for multi-turn identity image editing.
One chat per user - replaced when starting a new image generation.

The chat_history field stores serialized Gemini Content objects as JSON.
Images and thought signatures are automatically base64 encoded/decoded
by the Google genai SDK's pydantic models.
"""

import uuid

from django.db import models


class IdentityImageChat(models.Model):
    """
    Persists Gemini chat state for multi-turn identity image editing.

    One chat per user - replaced when starting a new image generation.
    The chat history contains all messages, generated images, and thought
    signatures needed to continue the conversation.

    Related to:
    - apps.users.models.User (OneToOne via user field)
    - apps.identities.models.Identity (FK via identity field)
    """

    # -------------------------------------------------------------------------
    # Primary Key
    # -------------------------------------------------------------------------

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique identifier for this object.",
    )

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------

    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="identity_image_chat",
        help_text="The user this chat session belongs to. One chat per user.",
    )

    identity = models.ForeignKey(
        "identities.Identity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="image_chats",
        help_text="The identity this chat is generating images for.",
    )

    # -------------------------------------------------------------------------
    # Chat State
    # -------------------------------------------------------------------------

    chat_history = models.JSONField(
        default=list,
        help_text="Serialized Gemini chat history (list of Content objects as JSON). "
        "Includes messages, generated images (base64), and thought signatures.",
    )

    # -------------------------------------------------------------------------
    # Timestamps
    # -------------------------------------------------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp when the chat session was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Timestamp when the chat session was last updated."
    )

    class Meta:
        verbose_name = "Identity Image Chat"
        verbose_name_plural = "Identity Image Chats"

    def __str__(self) -> str:
        identity_name = self.identity.name if self.identity else "No identity"
        return f"ImageChat for {self.user.email} - {identity_name}"
