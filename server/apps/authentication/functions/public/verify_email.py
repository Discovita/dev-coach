"""
verify_email

Validate an email-verification token and mark the user's email verified.
"""

from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.utils import AuthErrorMessages, is_token_expired
from apps.users.models import User
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


class VerificationInvalidError(Exception):
    """Raised when the verification token does not match any user."""


class VerificationExpiredError(Exception):
    """Raised when the verification token has expired."""


def verify_email(token: str) -> dict:
    """
    Validate a verification token, mark the email verified, and clear the token.

    Args:
        token: Verification token from the verify-email URL.

    Returns:
        Dict with ``message``, ``user_id``, and ``tokens`` (refresh/access) so
        the caller is logged in immediately on successful verification.

    Raises:
        VerificationInvalidError: If no user matches the token.
        VerificationExpiredError: If the token has expired.
    """
    try:
        user = User.objects.get(verification_token=token)
    except User.DoesNotExist:
        log.warning("Email verification attempt with invalid token")
        raise VerificationInvalidError(AuthErrorMessages.VERIFICATION_INVALID)

    if is_token_expired(user):
        log.warning("Email verification attempt with expired token for %s", user.email)
        raise VerificationExpiredError(AuthErrorMessages.VERIFICATION_EXPIRED)

    user.is_email_verified = True
    user.verification_token = ""
    user.email_verification_sent_at = None
    user.save()

    refresh = RefreshToken.for_user(user)

    log.info("Email verified for user %s", user.email)
    return {
        "message": "Email verified successfully",
        "user_id": user.id,
        "tokens": {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        },
    }
