from rest_framework import serializers


class CoachResponseSerializer(serializers.Serializer):
    """Serializer for the response from the coach endpoint."""

    message = serializers.CharField(
        allow_blank=True,
        help_text=(
            "Coach's response message. Empty string when the skip-LLM rule "
            "fires (e.g., START_BREAK or END_BREAK returned a component) — "
            "the component IS the coach's response that turn, no text."
        ),
    )
    final_prompt = serializers.CharField(
        allow_blank=True,
        help_text=(
            "The final prompt used to generate the coach's response. Empty "
            "string when the skip-LLM rule fires (no LLM call, no prompt)."
        ),
    )
    component = serializers.JSONField(
        required=False,
        help_text="Optional component configuration for frontend rendering.",
    )
    on_break = serializers.BooleanField(
        help_text=(
            "True iff the user has an open Break row "
            "(`ended_at IS NULL`) after this turn. Drives the frontend "
            "composer-disable rule."
        ),
    )
