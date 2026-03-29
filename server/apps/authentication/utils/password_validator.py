"""
Password strength validator for registration and password reset flows.
"""

import re

from django.core.exceptions import ValidationError

from apps.authentication.utils.auth_error_messages import AuthErrorMessages

MIN_PASSWORD_LENGTH = 8


def validate_password(password: str) -> None:
    """
    Validate password against strength requirements.

    Checks minimum length (8), uppercase letter, digit, and special character.

    Args:
        password: Password string to validate.

    Raises:
        ValidationError: If password doesn't meet requirements.
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(
            AuthErrorMessages.PASSWORD_TOO_SHORT.format(min_length=MIN_PASSWORD_LENGTH)
        )
    if not any(c.isupper() for c in password):
        raise ValidationError(AuthErrorMessages.PASSWORD_MISSING_UPPERCASE)
    if not any(c.isdigit() for c in password):
        raise ValidationError(AuthErrorMessages.PASSWORD_MISSING_NUMBER)
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError(AuthErrorMessages.PASSWORD_MISSING_SPECIAL)
