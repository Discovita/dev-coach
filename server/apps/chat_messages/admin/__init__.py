"""
Chat message admin configuration.

Exports:
    ChatMessageAdmin: Read-only Django admin for ChatMessage.
"""

from apps.chat_messages.admin.chat_message_admin import ChatMessageAdmin

__all__ = [
    "ChatMessageAdmin",
]
