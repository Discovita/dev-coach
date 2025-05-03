"""
Authentication utilities for error handling, validation, and response formatting.
"""

from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import ValidationError
import re
from typing import TypedDict


class AuthErrorMessages:
    """Standardized error messages for authentication flows."""
    INVALID_CREDENTIALS = "Invalid email or password"
    EMAIL_NOT_VERIFIED = "Please verify your email before logging in"
    EMAIL_EXISTS = "This email already has an account. Try signing in"
    INVALID_EMAIL_FORMAT = "Enter a valid email address"
    INVALID_PASSWORD_FORMAT = "Password must be at least 8 characters and contain uppercase, lowercase, number, and special character"
    PASSWORDS_NOT_MATCH = "Password fields don't match"
    EMAIL_SEND_FAILED = "Account created but verification email could not be sent"
    VERIFICATION_EXPIRED = "Verification link has expired"
    VERIFICATION_INVALID = "Invalid verification link"
    PASSWORD_TOO_SHORT = "Password must be at least {min_length} characters long"
    PASSWORD_MISSING_UPPERCASE = "Password must contain at least one uppercase letter"
    PASSWORD_MISSING_NUMBER = "Password must contain at least one number"
    PASSWORD_MISSING_SPECIAL = "Password must contain at least one special character"
    EMAIL_ALREADY_VERIFIED = "Email is already verified"
    UNEXPECTED_ERROR = "An unexpected error occurred. Please try again."


class ResponseData(TypedDict, total=False):
    """Type hints for response data."""
    success: bool
    message: str
    error: str
    user: dict
    tokens: dict
    email_sent: bool


def error_response(message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> Response:
    """
    Create a standardized error response.
    
    Args:
        message: Error message to return
        status_code: HTTP status code (default: 400)
    
    Returns:
        Response object with success=false and error message
    """
    return Response(
        {
            "success": False,
            "error": message
        },
        status=status_code
    )


def success_response(data: ResponseData, status_code: int = status.HTTP_200_OK) -> Response:
    """
    Create a standardized success response.
    
    Args:
        data: Response data to return (can include message, user, tokens, email_sent)
        status_code: HTTP status code (default: 200)
    
    Returns:
        Response object with success=true and flattened data
    """
    response_data = {"success": True}
    
    # Flatten any nested data and add to response
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict) and key == "data":
                # If there's a nested data object, flatten it
                response_data.update(value)
            else:
                response_data[key] = value
    
    return Response(response_data, status=status_code)


class PasswordValidator:
    """
    Validates password strength requirements.
    
    Requirements:
    - Minimum length (default: 8)
    - Uppercase letter (optional)
    - Number (optional)
    - Special character (optional)
    """
    
    def __init__(
        self,
        min_length: int = 8,
        require_uppercase: bool = True,
        require_number: bool = True,
        require_special: bool = True,
    ):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_number = require_number
        self.require_special = require_special

    def validate(self, password: str) -> None:
        """
        Validate password against requirements.
        
        Args:
            password: Password string to validate
            
        Raises:
            ValidationError: If password doesn't meet requirements
        """
        if len(password) < self.min_length:
            raise ValidationError(
                AuthErrorMessages.PASSWORD_TOO_SHORT.format(min_length=self.min_length)
            )
        if self.require_uppercase and not any(c.isupper() for c in password):
            raise ValidationError(AuthErrorMessages.PASSWORD_MISSING_UPPERCASE)
        if self.require_number and not any(c.isdigit() for c in password):
            raise ValidationError(AuthErrorMessages.PASSWORD_MISSING_NUMBER)
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(AuthErrorMessages.PASSWORD_MISSING_SPECIAL) 