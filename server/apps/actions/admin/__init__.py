"""
Actions - Admin package

Django loads `apps.actions.admin` as a package when this directory exists.
Register ModelAdmin classes at import time.
"""

from apps.actions.admin.action_admin import register_action_admin

register_action_admin()

__all__ = ["register_action_admin"]
