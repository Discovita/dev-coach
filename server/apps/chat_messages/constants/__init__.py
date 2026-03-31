"""
Chat message constants.

Exports:
    INITIAL_MESSAGE: Current welcome message sent to new users.
    INITIAL_MESSAGE_OLD: Original identity-creation exercise message (preserved for reference).
"""

from apps.chat_messages.constants.initial_messages import (
    INITIAL_MESSAGE,
    INITIAL_MESSAGE_OLD,
)

__all__ = [
    "INITIAL_MESSAGE",
    "INITIAL_MESSAGE_OLD",
]
