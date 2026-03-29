"""
forgot_password

Initiate the password-reset flow by generating a token and sending an email.
"""

from apps.authentication.utils import (
    AuthErrorMessages,
    generate_verification_token,
    send_password_reset_email,
)
from apps.users.models import User
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")

_GENERIC_MESSAGE = "If an account exists, a password reset email will be sent"


def forgot_password(email: str) -> dict:
    """
    Look up the user, generate a reset token, and send the email.

    Returns a generic success message regardless of whether the email
    exists to avoid leaking account existence.

    Args:
        email: Email address from the request.

    Returns:
        Dict with ``message`` and ``email_sent`` keys.

    Raises:
        RuntimeError: If the email exists but sending fails (caller
            decides the HTTP response).
    """
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        log.info("Forgot-password for non-existent email %s", email)
        return {"message": _GENERIC_MESSAGE, "email_sent": False}

    generate_verification_token(user)
    email_sent = send_password_reset_email(user)

    if not email_sent:
        log.error("Failed to send password reset email to %s", email)
        raise RuntimeError(AuthErrorMessages.EMAIL_SEND_FAILED)

    log.info("Password reset email sent to %s", email)
    return {"message": "Password reset email sent", "email_sent": True}
