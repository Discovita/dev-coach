"""
Authentication serializers for handling user data validation and transformation.

This module contains serializers for:
- User registration with email verification
- Login with credentials validation
- LTI launch request validation
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from apps.users.models import User
from apps.authentication.utils import PasswordValidator, AuthErrorMessages


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Validates:
    - Password requirements via PasswordValidator

    Fields:
    - email: User's email (must be unique)
    - password: User's password (must meet requirements)
    
    Returns:
    - On success: Validated data
    - On error: Formatted error message matching interface:
      {
          "success": false,
          "error": "Error message string"
      }
    """

    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("email", "password")

    def validate(self, data):
        """
        Validate password requirements.

        Raises:
            ValidationError: If password doesn't meet requirements
            - Too short (< 8 characters)
            - Missing uppercase letter
            - Missing number
            - Missing special character
            
        Returns:
            dict: Validated data if validation passes
        """
        password = data.get("password")
        validator = PasswordValidator()

        try:
            validator.validate(password)
        except ValidationError as e:
            # Raise a dict with 'error' key to match the interface
            raise serializers.ValidationError({
                'error': str(e.message)
            })

        return data



class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.

    Validates:
    - User credentials (email/password)
    - Account is active
    - Email is verified
    """

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        """
        Validate user credentials and account status.

        Raises:
            ValidationError: If credentials are invalid
        """
        user = authenticate(email=data["email"], password=data["password"])
        if not user:
            raise serializers.ValidationError(AuthErrorMessages.INVALID_CREDENTIALS)

        data["user"] = user
        return data


class ResourceLinkSerializer(serializers.Serializer):
    """Serializer for the resourceLink object in LTI requests."""
    id = serializers.CharField()
