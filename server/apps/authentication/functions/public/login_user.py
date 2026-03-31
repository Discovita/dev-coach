"""
login_user

Issue JWT tokens for an already-authenticated user.
"""

from typing import Any

from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


def login_user(user: User) -> dict[str, Any]:
    """
    Generate JWT tokens for an authenticated user.

    Args:
        user: User instance (already authenticated by LoginSerializer).

    Returns:
        Dict with ``user_id``, ``tokens.refresh``, and ``tokens.access``.
    """
    refresh = RefreshToken.for_user(user)

    log.info("User %s logged in", user.email)

    return {
        "user_id": user.id,
        "tokens": {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        },
    }
