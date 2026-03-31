"""
ChatMessage serializer.

Used by:
    - apps.users.views.user_viewset.UserViewSet (chat_messages endpoint)
    - apps.users.views.test_user_viewset.TestUserViewSet (chat_messages endpoint)
    - apps.users.serializers.user_serializer.UserSerializer (nested)
    - apps.actions.serializers.action_serializer.ActionSerializer (nested)
"""

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
        help_text="Optional component configuration for persistent rendering (stored as JSON).",
    )

    class Meta:
        model = ChatMessage
        fields = (
            "id",
            "role",
            "content",
            "timestamp",
            "component_config",
        )
        read_only_fields = (
            "id",
            "role",
            "content",
            "timestamp",
        )
