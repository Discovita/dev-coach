"""
Centralized DRF permission classes.

Shared across all apps. One permission class per file.

Usage:
    from permissions import IsAdminUser
"""

from permissions.is_admin_user import IsAdminUser
from permissions.is_super_user import IsSuperUser

__all__ = ["IsAdminUser", "IsSuperUser"]
