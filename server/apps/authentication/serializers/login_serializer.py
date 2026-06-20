"""
Request serializer for user login.
"""

from django.contrib.auth import authenticate
from rest_framework import serializers

from apps.authentication.utils.auth_error_messages import AuthErrorMessages


class LoginSerializer(serializers.Serializer):
    """
    Validates login credentials and attaches the authenticated User.

    On successful validation, ``validated_data["user"]`` contains the
    authenticated User instance.
    """

    email = serializers.EmailField(help_text="User's registered email address.")
    password = serializers.CharField(help_text="User's password.")

    def validate(self, data: dict) -> dict:
        """Authenticate credentials and require a verified email."""
        user = authenticate(email=data["email"], password=data["password"])
        if not user:
            raise serializers.ValidationError(AuthErrorMessages.INVALID_CREDENTIALS)
        if not user.is_email_verified:
            raise serializers.ValidationError(AuthErrorMessages.EMAIL_NOT_VERIFIED)
        data["user"] = user
        return data
