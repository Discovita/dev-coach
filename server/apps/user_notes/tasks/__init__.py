"""
Celery tasks for the user_notes app.

Exports:
    extract_user_notes: Async task that runs the Sentinel agent to extract notes from a chat message.
"""

from apps.user_notes.tasks.extract_user_notes import extract_user_notes

__all__ = ["extract_user_notes"]
