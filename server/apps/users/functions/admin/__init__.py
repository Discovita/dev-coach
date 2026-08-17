"""
Admin functions for the users app.

These functions handle business logic for admin-only endpoints.
"""

from apps.users.functions.admin.delete_user_account import delete_user_account

__all__ = ["delete_user_account"]
