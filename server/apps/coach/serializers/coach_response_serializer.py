from rest_framework import serializers


class CoachResponseSerializer(serializers.Serializer):
    """Serializer for the response from the coach endpoint."""

    message = serializers.CharField(help_text="Coach's response message.")
    final_prompt = serializers.CharField(
        help_text="The final prompt used to generate the coach's response."
    )
    component = serializers.JSONField(
        required=False,
        help_text="Optional component configuration for frontend rendering.",
    )
