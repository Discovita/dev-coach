"""
UserSerializer for complete user data serialization.

Includes nested related data (identities, coach state, chat messages).

See: apps/users/serializers/__init__.py
"""

from rest_framework import serializers

from apps.chat_messages.serializers import ChatMessageSerializer
from apps.coach_states.serializers import CoachStateSerializer
from apps.identities.serializers import IdentitySerializer
from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Full User serializer with nested related data.

    Used for the ``me/complete`` endpoint and anywhere the frontend
    needs the full user object with identities, coach state, and
    chat messages.
    """

    groups = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    user_permissions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    identities = IdentitySerializer(many=True, read_only=True)
    coach_state = CoachStateSerializer(read_only=True)
    chat_messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_superuser",
            "is_staff",
            "last_login",
            "created_at",
            "updated_at",
            "groups",
            "user_permissions",
            "identities",
            "coach_state",
            "chat_messages",
            "gender",
            "skin_tone",
            "hair_color",
            "eye_color",
            "height",
            "build",
            "age_range",
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
