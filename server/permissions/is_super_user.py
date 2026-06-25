"""
IsSuperUser — permission class for super-admin-only endpoints.

Grants access only to users with is_superuser=True. Stricter than
``IsAdminUser`` (which also allows is_staff). Use for capabilities
reserved for super admins:

    from permissions import IsSuperUser

    @decorators.action(detail=True, methods=["patch"], permission_classes=[IsSuperUser])
    def sensitive_action(self, request, pk=None):
        ...
"""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class IsSuperUser(BasePermission):
    """Allows access only to super admins (is_superuser=True)."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "is_superuser", False)
        )
