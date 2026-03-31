"""
Standardized error message constants for authentication flows.
"""


class AuthErrorMessages:
    """
    Standardized error messages for authentication flows.

    Used by serializers, functions, and the ViewSet to return consistent
    user-facing error strings.
    """

    INVALID_CREDENTIALS = "Invalid email or password"
    EMAIL_NOT_VERIFIED = "Please verify your email before logging in"
    EMAIL_EXISTS = "This email already has an account. Try signing in"
    INVALID_EMAIL_FORMAT = "Enter a valid email address"
    INVALID_PASSWORD_FORMAT = (
        "Password must be at least 8 characters and contain "
        "uppercase, lowercase, number, and special character"
    )
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
