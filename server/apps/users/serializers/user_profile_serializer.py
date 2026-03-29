"""
UserProfileSerializer for lightweight user profile data.

Does not include nested related objects (identities, coach state, etc.).

See: apps/users/serializers/__init__.py
"""

from rest_framework import serializers

from apps.users.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Lightweight User serializer for profile endpoints.

    Used for ``me/`` GET and PATCH — returns core user fields and
    appearance preferences without nested relations.
    """

    groups = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    user_permissions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

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
        )
