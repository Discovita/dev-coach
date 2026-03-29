"""
Read-only serializer for Action API responses.
"""

from rest_framework import serializers

from apps.actions.models import Action
from apps.chat_messages.serializer import ChatMessageSerializer


class ActionSerializer(serializers.ModelSerializer):
    """
    Serializes Action for read-only detail responses.

    Used by UserViewSet and TestUserViewSet to return actions
    with nested coach message context.
    """

    coach_message = ChatMessageSerializer(read_only=True)

    action_type_display = serializers.CharField(
        source="get_action_type_display",
        read_only=True,
        help_text="Human-readable action type label.",
    )

    timestamp_formatted = serializers.SerializerMethodField(
        help_text="Timestamp formatted for display (YYYY-MM-DD HH:MM:SS).",
    )

    class Meta:
        model = Action
        fields = [
            "id",
            "user",
            "action_type",
            "action_type_display",
            "parameters",
            "result_summary",
            "timestamp",
            "updated_at",
            "timestamp_formatted",
            "coach_message",
            "test_scenario",
        ]
        read_only_fields = fields

    def get_timestamp_formatted(self, obj: Action) -> str:
        return obj.timestamp.strftime("%Y-%m-%d %H:%M:%S")
