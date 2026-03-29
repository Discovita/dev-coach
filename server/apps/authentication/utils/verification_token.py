"""
Verification token generation and expiry checking.

Operates on User.verification_token and User.email_verification_sent_at fields.
"""

import secrets
from datetime import datetime, timedelta

from apps.users.models import User
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")

TOKEN_EXPIRY_HOURS = 24


def generate_verification_token(user: User) -> str:
    """
    Generate a cryptographically secure verification token and persist it.

    Args:
        user: User to generate token for.

    Returns:
        The generated hex token string.

    Raises:
        Exception: If the token cannot be saved.
    """
    try:
        user.verification_token = secrets.token_hex(32)
        user.email_verification_sent_at = datetime.now().astimezone()
        user.save()
        log.info("Generated verification token for user %s", user.email)
        return user.verification_token
    except Exception as e:
        log.error(
            "Failed to generate verification token for user %s: %s",
            user.email,
            e,
        )
        raise


def is_token_expired(user: User) -> bool:
    """
    Check whether the user's verification token has expired.

    Args:
        user: User whose token to check.

    Returns:
        True if expired or no timestamp exists, False otherwise.
    """
    if not user.email_verification_sent_at:
        log.warning("No verification timestamp for user %s", user.email)
        return True

    expiry_time = user.email_verification_sent_at + timedelta(hours=TOKEN_EXPIRY_HOURS)
    is_expired = datetime.now().astimezone() > expiry_time

    if is_expired:
        log.warning("Verification token expired for user %s", user.email)
    else:
        log.info("Verification token still valid for user %s", user.email)

    return is_expired
