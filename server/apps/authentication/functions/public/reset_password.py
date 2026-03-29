"""
reset_password

Validate a reset token and update the user's password.
"""

from apps.authentication.utils import AuthErrorMessages, is_token_expired
from apps.users.models import User
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


class TokenExpiredError(Exception):
    """Raised when the verification token has expired."""


class TokenInvalidError(Exception):
    """Raised when the verification token does not match any user."""


def reset_password(token: str, new_password: str) -> dict:
    """
    Validate a reset token, update the user's password, and clear the token.

    Args:
        token: Verification token from the reset URL.
        new_password: The new password to set.

    Returns:
        Dict with a ``message`` key on success.

    Raises:
        TokenInvalidError: If no user matches the token.
        TokenExpiredError: If the token has expired.
    """
    try:
        user = User.objects.get(verification_token=token)
    except User.DoesNotExist:
        log.warning("Reset attempt with invalid token")
        raise TokenInvalidError(AuthErrorMessages.VERIFICATION_INVALID)

    if is_token_expired(user):
        log.warning("Reset attempt with expired token for user %s", user.email)
        raise TokenExpiredError(AuthErrorMessages.VERIFICATION_EXPIRED)

    user.set_password(new_password)
    user.verification_token = ""
    user.email_verification_sent_at = None
    user.save()

    log.info("Password reset completed for user %s", user.email)
    return {"message": "Password updated successfully"}
