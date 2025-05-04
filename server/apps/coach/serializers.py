from rest_framework import serializers

class CoachRequestSerializer(serializers.Serializer):
    """
    Serializer for incoming user message to the coach endpoint.
    Fields:
    - message: The user's message to the coach (required).
    """
    message = serializers.CharField(help_text="User's message to the coach.")

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
    coach_state = serializers.JSONField(help_text="Updated state of the coaching session.")
    final_prompt = serializers.CharField(help_text="The final prompt used to generate the coach's response.")
    actions = serializers.ListField(
        child=serializers.DictField(),
        default=list,
        help_text="Actions performed (list of dicts, can be empty)."
    ) 