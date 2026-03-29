"""
Django admin configuration for the user_notes app.

Exports:
    UserNoteAdmin: Admin interface for managing user notes.
"""

from apps.user_notes.admin.user_note_admin import UserNoteAdmin

__all__ = ["UserNoteAdmin"]
