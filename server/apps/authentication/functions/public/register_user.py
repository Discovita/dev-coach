"""
register_user

Create a new user account and return JWT tokens.
"""

from typing import Any

from rest_framework_simplejwt.tokens import RefreshToken

from django.db import transaction

from apps.authentication.utils import send_verification_email
from apps.users.models import User
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


@transaction.atomic
def register_user(email: str, password: str) -> dict[str, Any]:
    """
    Create a new user, send a verification email, and issue JWT tokens.

    Email verification is best-effort and does NOT gate access: the account is
    active and logged in immediately. A failed verification send is logged but
    does not fail registration.

    Args:
        email: Validated email address (unique check done by serializer).
        password: Validated password (strength check done by serializer).

    Returns:
        Dict with ``user_id``, ``tokens.refresh``, and ``tokens.access``.

    Raises:
        Exception: If user creation or token generation fails.
    """
    user = User.objects.create_user(email=email, password=password)
    refresh = RefreshToken.for_user(user)

    log.info("Registered new user %s", email)

    # Best-effort verification email — never block registration on delivery.
    if not send_verification_email(user):
        log.warning("Verification email could not be sent for new user %s", email)

    return {
        "user_id": user.id,
        "tokens": {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        },
    }
