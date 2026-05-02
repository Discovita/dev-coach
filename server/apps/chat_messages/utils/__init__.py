"""
Chat message utilities.

Exports:
    add_chat_message: Create a new ChatMessage record for a user.
    ensure_initial_message_exists: Seed a user's chat with the welcome message.
"""

from apps.chat_messages.utils.add_chat_message import add_chat_message
from apps.chat_messages.utils.ensure_initial_message_exists import (
    ensure_initial_message_exists,
)

__all__ = [
    "add_chat_message",
    "ensure_initial_message_exists",
]
