"""
List serializer for Action collections (lighter payload than ActionSerializer).
"""

from rest_framework import serializers

from apps.actions.models import Action


class ActionListSerializer(serializers.ModelSerializer):
    """
    Simplified Action representation for list endpoints.
    """

    action_type_display = serializers.CharField(
        source="get_action_type_display",
        read_only=True,
        help_text="Human-readable action type label.",
    )

    coach_message_preview = serializers.SerializerMethodField(
        help_text="First 100 characters of the triggering coach message.",
    )

    class Meta:
        model = Action
        fields = [
            "id",
            "action_type",
            "action_type_display",
            "result_summary",
            "timestamp",
            "coach_message_preview",
        ]
        read_only_fields = fields

    def get_coach_message_preview(self, obj: Action) -> str | None:
        if obj.coach_message:
            content = obj.coach_message.content
            return content[:100] + "..." if len(content) > 100 else content
        return None
