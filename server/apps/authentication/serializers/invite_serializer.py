"""
Serializers for the invite flow.

- ``CreateInviteSerializer`` — admin input to send an invite (email).
- ``InviteSerializer`` — admin output: an invite row with derived status.
- ``RegisterViaInviteSerializer`` — public input to accept an invite
  (token + password, password strength-checked).
"""

from django.core.exceptions import ValidationError
from rest_framework import serializers

from apps.authentication.models import Invite
from apps.authentication.utils.password_validator import validate_password


class CreateInviteSerializer(serializers.Serializer):
    """Validates the email an admin wants to invite."""

    email = serializers.EmailField()

    def validate_email(self, value: str) -> str:
        """Normalise to lowercase; uniqueness handled by the view."""
        return value.strip().lower()


class InviteSerializer(serializers.ModelSerializer):
    """Read serializer for the admin invite list."""

    status = serializers.SerializerMethodField()
    invited_by_email = serializers.SerializerMethodField()

    class Meta:
        model = Invite
        fields = (
            "id",
            "email",
            "status",
            "expires_at",
            "accepted_at",
            "invited_by_email",
            "created_at",
        )

    def get_status(self, obj: Invite) -> str:
        if obj.is_accepted:
            return "accepted"
        if obj.is_expired:
            return "expired"
        return "pending"

    def get_invited_by_email(self, obj: Invite) -> str | None:
        return obj.invited_by.email if obj.invited_by else None


class RegisterViaInviteSerializer(serializers.Serializer):
    """Validates a register-via-invite submission."""

    token = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate_password(self, value: str) -> str:
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e.message))
        return value
