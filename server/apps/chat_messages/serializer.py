from rest_framework import serializers
from apps.chat_messages.models import ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for ChatMessage model.
    
    Handles serialization of chat messages including optional component configurations.
    Component configurations are stored as JSON and can be used for persistent rendering.
    """
    
    component_config = serializers.JSONField(
        required=False,
        allow_null=True,
        help_text="Optional component configuration for persistent rendering (stored as JSON)."
    )
    
    class Meta:
        model = ChatMessage
        fields = (
            "id",  # Unique identifier for the message
            "role",  # Role of the message sender (user or coach)
            "content",  # Content of the message
            "timestamp",  # When the message was sent
            "component_config",  # Optional component configuration for persistent rendering
        )
        read_only_fields = (
            "id",  # Unique identifier for the message
            "role",  # Role of the message sender (user or coach)
            "content",  # Content of the message
            "timestamp",  # When the message was sent
        )
