"""
Request serializer for user registration.
"""

from django.core.exceptions import ValidationError
from rest_framework import serializers

from apps.authentication.utils.auth_error_messages import AuthErrorMessages
from apps.authentication.utils.password_validator import validate_password
from apps.users.models import User


class RegisterSerializer(serializers.ModelSerializer):
    """
    Validates registration input: email uniqueness and password strength.

    Fields:
    - email: Must be a valid, unique email address.
    - password: Must meet validate_password requirements (write-only).
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text="User password (min 8 chars, uppercase, number, special char).",
    )

    class Meta:
        model = User
        fields = ("email", "password")

    def validate_email(self, value: str) -> str:
        """Reject emails that are already registered."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(AuthErrorMessages.EMAIL_EXISTS)
        return value

    def validate_password(self, value: str) -> str:
        """Run password through strength requirements."""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e.message))
        return value
