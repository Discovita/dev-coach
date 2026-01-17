"""
UserProfileSerializer for basic user profile data.

This serializer provides a lightweight representation of user data
without nested related objects.
"""

from rest_framework import serializers

from apps.users.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for User model for profile data.
    Used for: Profile data serialization
    """

    # Groups and permissions as lists of IDs
    groups = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    user_permissions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        # Expose all safe fields for the frontend
        fields = (
            "id",  # User ID
            "email",  # Email address
            "first_name",  # First name
            "last_name",  # Last name
            "is_active",  # Active status
            "is_superuser",  # Django superuser flag
            "is_staff",  # Staff/admin page access
            "last_login",  # Last login timestamp
            "created_at",  # Created at timestamp
            "updated_at",  # Updated at timestamp
            "groups",  # Group memberships (IDs)
            "user_permissions",  # User permissions (IDs)
            # Appearance/visualization preferences for image generation
            "gender",  # Gender preference
            "skin_tone",  # Skin tone preference
            "hair_color",  # Hair color preference
            "eye_color",  # Eye color preference
            "height",  # Height preference
            "build",  # Build preference
            "age_range",  # Age range preference
        )
        read_only_fields = (
            "created_at",
            "updated_at",
            "groups",
            "user_permissions",
            "date_joined",
            "last_login",
            "email_verification_sent_at",
        )

