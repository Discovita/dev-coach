"""
Query parameter validation for GET .../actions/by-coach-message.
"""

from rest_framework import serializers


class ByCoachMessageActionsQuerySerializer(serializers.Serializer):
    """
    Validates query params for listing actions tied to one coach message.
    """

    message_id = serializers.UUIDField(
        help_text="ChatMessage primary key (UUID).",
    )
