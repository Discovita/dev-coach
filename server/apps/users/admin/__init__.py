"""
Django admin configuration for the users app.

Exports:
    UserAdmin: Admin interface for managing users.
"""

from apps.users.admin.user_admin import UserAdmin

__all__ = ["UserAdmin"]
