"""
UserSerializer for complete user data serialization.

This serializer includes nested related data like identities, coach state, and chat messages.
"""

from rest_framework import serializers

from apps.users.models import User
from apps.identities.serializer import IdentitySerializer
from apps.coach_states.serializer import CoachStateSerializer
from apps.chat_messages.serializer import ChatMessageSerializer


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
    # Include identities as a nested serializer
    identities = IdentitySerializer(many=True, read_only=True)
    # Include coach state as a nested serializer
    coach_state = CoachStateSerializer(read_only=True)
    # Include chat messages as a nested serializer
    chat_messages = ChatMessageSerializer(many=True, read_only=True)

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
            "identities",  # User's identities
            "coach_state",  # User's coach state
            "chat_messages",  # User's chat messages
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
            "identities",
            "coach_state",
            "chat_messages",
        )

