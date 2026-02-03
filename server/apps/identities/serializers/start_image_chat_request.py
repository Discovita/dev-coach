"""
StartImageChatRequest Serializer

Validates request data for starting a new image chat session.
"""

from rest_framework import serializers


class StartImageChatRequestSerializer(serializers.Serializer):
    """
    Validates request data for the start-image-chat endpoint.

    For admin endpoints, user_id is required.
    For user endpoints, user_id is not included (uses authenticated user).
    """

    identity_id = serializers.UUIDField(
        help_text="UUID of the identity to generate an image for"
    )

    user_id = serializers.UUIDField(
        required=False,
        help_text="UUID of the user (admin only - omit for user endpoints)"
    )

    additional_prompt = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Optional additional instructions for image generation"
    )
