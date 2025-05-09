from rest_framework import serializers
from enums.ai import AIModel
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


class CoachRequestSerializer(serializers.Serializer):
    """
    Serializer for incoming user message to the coach endpoint.
    Fields:
    - message: The user's message to the coach (required).
    - model_name: (Optional) The name of the AI model to use. If not provided, defaults to GPT-4o.
    """

    message = serializers.CharField(help_text="User's message to the coach.")
    model_name = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional model name. If not provided, uses default.",
    )

    def get_model(self) -> "AIModel":
        """
        Return the AIModel instance for this request.
        Uses the model_name if provided, otherwise returns the default model (GPT-4o).
        """
        return AIModel.get_or_default(self.validated_data.get("model_name"))


class CoachResponseSerializer(serializers.Serializer):
    """
    Serializer for the response from the coach endpoint.
    Fields:
    - message: The coach's response message.
    - coach_state: The updated state of the coaching session (as dict for now).
    - final_prompt: The final prompt used to generate the coach's response.
    - actions: List of actions performed (list of dicts, can be empty).
    """

    message = serializers.CharField(help_text="Coach's response message.")
    coach_state = serializers.JSONField(
        help_text="Updated state of the coaching session."
    )
    final_prompt = serializers.CharField(
        help_text="The final prompt used to generate the coach's response."
    )
    actions = serializers.ListField(
        child=serializers.DictField(),
        default=list,
        help_text="Actions performed (list of dicts, can be empty).",
    )
