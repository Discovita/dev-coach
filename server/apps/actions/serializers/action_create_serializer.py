"""
Writable serializer for creating Action rows (e.g. action handler).
"""

from rest_framework import serializers

from apps.actions.models import Action


class ActionCreateSerializer(serializers.ModelSerializer):
    """
    Validates payloads when persisting new Action instances.
    """

    class Meta:
        model = Action
        fields = [
            "user",
            "action_type",
            "parameters",
            "result_summary",
            "coach_message",
            "test_scenario",
        ]

    def validate_parameters(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Parameters must be a JSON object.")
        return value

    def validate(self, data):
        coach_message = data.get("coach_message")
        if coach_message and coach_message.role != "coach":
            raise serializers.ValidationError(
                "Actions can only be linked to coach messages."
            )
        return data
