"""
Chat message signals.

Exports:
    trigger_sentinel_on_user_message: Post-save handler that schedules
        user notes extraction when a new user message is created.
"""

from apps.chat_messages.signals.trigger_sentinel_on_user_message import (
    trigger_sentinel_on_user_message,
)

__all__ = [
    "trigger_sentinel_on_user_message",
]
