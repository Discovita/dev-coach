"""
Centralized DRF permission classes.

Shared across all apps. One permission class per file.

Usage:
    from permissions import IsAdminUser
"""

from permissions.is_admin_user import IsAdminUser

__all__ = ["IsAdminUser"]
