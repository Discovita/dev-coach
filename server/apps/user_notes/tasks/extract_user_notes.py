"""
Celery task that delegates to the Sentinel agent for user-note extraction.

See: apps/user_notes/tasks/__init__.py
"""

from celery import shared_task

from apps.chat_messages.models import ChatMessage
from services.sentinel.sentinel import Sentinel


@shared_task
def extract_user_notes(chat_message_id: str) -> None:
    """
    Run the Sentinel agent on *chat_message_id* to extract user notes.

    Invoked asynchronously (via Celery) whenever a new user message
    is received, triggered by the ``trigger_sentinel_on_user_message``
    signal in the ``chat_messages`` app.
    """
    user_msg = ChatMessage.objects.get(id=chat_message_id)
    sentinel = Sentinel(user_msg.user)
    sentinel.extract_notes(user_msg)
