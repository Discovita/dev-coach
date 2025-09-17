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
    - user_id: (Optional) The user ID to act as (admin only). If not provided, uses request.user.
    """

    message = serializers.CharField(help_text="User's message to the coach.")
    model_name = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional model name. If not provided, uses default.",
    )
    user_id = serializers.UUIDField(
        required=False,
        help_text="Optional user ID to act as (admin only). If not provided, uses request.user.",
    )
    actions = serializers.ListField(
        required=False,
        allow_null=True,
        allow_empty=True,
        child=serializers.DictField(),
        help_text=(
            "List of actions to execute in order. Each item should be an object "
            "with 'action' (str) and 'params' (object). Can be sent alongside message."
        ),
    )

    def get_model(self) -> "AIModel":
        """
        Return the AIModel instance for this request.
        Uses the model_name if provided, otherwise returns the default model (GPT-4o).
        """
        return AIModel.get_or_default(self.validated_data.get("model_name"))

    def validate(self, attrs):
        """
        Require at least one of the following fields:
        - message: string-based user input
        - actions: array of { action: str, params: object }
        """
        message = attrs.get("message")
        actions = attrs.get("actions")

        if not message and not actions:
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "Provide at least one of: 'message' or 'actions'."
                    ]
                }
            )

        if actions is not None:
            # Lightweight structure checks; deep validation happens in the Action Handler
            for idx, item in enumerate(actions):
                if not isinstance(item, dict):
                    raise serializers.ValidationError(
                        {"actions": f"Item {idx} must be an object."}
                    )
                if "action" not in item or not isinstance(item.get("action"), str):
                    raise serializers.ValidationError(
                        {"actions": f"Item {idx} must include 'action' (str)."}
                    )
                if "params" not in item:
                    raise serializers.ValidationError(
                        {"actions": f"Item {idx} must include 'params' (object)."}
                    )

        return attrs


class CoachResponseSerializer(serializers.Serializer):
    """
    Serializer for the response from the coach endpoint.
    Fields:
    - message: The coach's response message.
    - coach_state: The updated state of the coaching session (as dict for now).
    - final_prompt: The final prompt used to generate the coach's response.
    - actions: List of actions performed (list of dicts, can be empty).
    - chat_history: The latest chat history (list of messages, most recent last).
    - identities: The user's current identities (list of identity dicts).
    """

    message = serializers.CharField(help_text="Coach's response message.")
    final_prompt = serializers.CharField(
        help_text="The final prompt used to generate the coach's response."
    )
    component = serializers.JSONField(
        required=False,
        help_text="Optional component configuration for frontend rendering.",
    )
