from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.

    Used for:
    - Profile data serialization
    - User data in responses
    - About Me page (frontend)
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
            "date_joined",  # Date joined
            "created_at",  # Created at timestamp
            "updated_at",  # Updated at timestamp
            "groups",  # Group memberships (IDs)
            "user_permissions",  # User permissions (IDs)
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
