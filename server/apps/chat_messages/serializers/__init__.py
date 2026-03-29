"""
Chat message serializers.

Exports:
    ChatMessageSerializer: Read-only serializer for ChatMessage model
        (used by UserViewSet, TestUserViewSet, and ActionSerializer).
"""

from apps.chat_messages.serializers.chat_message_serializer import (
    ChatMessageSerializer,
)

__all__ = [
    "ChatMessageSerializer",
]
