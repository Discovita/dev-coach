"""
resend_verification

Re-send the email-verification message for an unverified account.
"""

from apps.authentication.utils import send_verification_email
from apps.users.models import User
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")

_GENERIC_MESSAGE = (
    "If an account exists and is unverified, a verification email will be sent"
)


def resend_verification(email: str) -> dict:
    """
    Look up the user and re-send a verification email if they are unverified.

    Returns a generic success message regardless of whether the email exists
    or is already verified, to avoid leaking account existence.

    Args:
        email: Email address from the request.

    Returns:
        Dict with ``message`` and ``email_sent`` keys.
    """
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        log.info("Resend-verification for non-existent email %s", email)
        return {"message": _GENERIC_MESSAGE, "email_sent": False}

    if user.is_email_verified:
        log.info("Resend-verification for already-verified email %s", email)
        return {"message": _GENERIC_MESSAGE, "email_sent": False}

    email_sent = send_verification_email(user)
    if email_sent:
        log.info("Verification email re-sent to %s", email)

    return {"message": _GENERIC_MESSAGE, "email_sent": email_sent}
