"""
register_user

Create a new user account and return JWT tokens.
"""

from typing import Any

from django.db import transaction

from apps.authentication.utils import send_verification_email
from apps.users.models import User
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


@transaction.atomic
def register_user(email: str, password: str) -> dict[str, Any]:
    """
    Create a new (unverified) user and send a verification email.

    Registration does NOT log the user in: no JWT tokens are issued. The user
    must verify their email before they can log in (see LoginSerializer). The
    verification send is best-effort — a delivery failure is reported via
    ``email_sent`` so the UI can offer a resend, but it does not fail
    registration or roll back the account.

    Args:
        email: Validated email address (unique check done by serializer).
        password: Validated password (strength check done by serializer).

    Returns:
        Dict with ``user_id`` and ``email_sent``.

    Raises:
        Exception: If user creation fails.
    """
    user = User.objects.create_user(email=email, password=password)

    log.info("Registered new user %s", email)

    email_sent = send_verification_email(user)
    if not email_sent:
        log.warning("Verification email could not be sent for new user %s", email)

    return {
        "user_id": user.id,
        "email_sent": email_sent,
    }
