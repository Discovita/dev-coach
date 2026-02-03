"""
ContinueImageChatRequest Serializer

Validates request data for continuing an image chat session.
"""

from rest_framework import serializers


class ContinueImageChatRequestSerializer(serializers.Serializer):
    """
    Validates request data for the continue-image-chat endpoint.

    For admin endpoints, user_id is required.
    For user endpoints, user_id is not included (uses authenticated user).
    """

    user_id = serializers.UUIDField(
        required=False,
        help_text="UUID of the user (admin only - omit for user endpoints)"
    )

    edit_prompt = serializers.CharField(
        help_text="The edit instruction (e.g., 'make the lighting warmer')"
    )

    def validate_edit_prompt(self, value: str) -> str:
        """Ensure edit prompt is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Edit prompt is required.")
        return value.strip()
