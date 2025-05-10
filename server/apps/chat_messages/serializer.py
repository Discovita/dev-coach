from rest_framework import serializers
from apps.chat_messages.models import ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = (
            "id",  # Unique identifier for the message
            "role",  # Role of the message sender (user or coach)
            "content",  # Content of the message
            "timestamp",  # When the message was sent
        )
        read_only_fields = (
            "id",  # Unique identifier for the message
            "role",  # Role of the message sender (user or coach)
            "content",  # Content of the message
            "timestamp",  # When the message was sent
        )
