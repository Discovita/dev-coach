"""
IsAdminUser — permission class for admin-only endpoints.

Grants access to users with is_staff=True or is_superuser=True.
Use on admin ViewSets:

    from permissions import IsAdminUser

    class AdminResourceViewSet(viewsets.GenericViewSet):
        permission_classes = [IsAuthenticated, IsAdminUser]
"""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAdminUser(BasePermission):
    """
    Allows access only to admin users (is_staff or is_superuser).

    This is the single source of truth for admin access checks.
    Always use this permission class instead of inline is_staff checks
    or DRF's built-in IsAdminUser (which only checks is_staff).
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (
                getattr(user, "is_staff", False) or getattr(user, "is_superuser", False)
            )
        )
