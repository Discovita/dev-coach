"""
Admin Identity Image Chat ViewSet

Admin endpoints for image generation chat sessions.
Allows admins to test image chat for any user.
"""

from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request

from apps.identities.serializers import (
    StartImageChatRequestSerializer,
    ContinueImageChatRequestSerializer,
)
from apps.identities.functions.admin import (
    admin_start_image_chat,
    admin_continue_image_chat,
)
from services.logger import configure_logging

log = configure_logging(__name__)


class AdminIdentityImageChatViewSet(viewsets.GenericViewSet):
    """
    Admin endpoints for identity image generation chat.

    Endpoints:
    - POST /api/v1/admin/identity-image-chat/start/   → start_chat()
    - POST /api/v1/admin/identity-image-chat/continue/ → continue_chat()
    """

    permission_classes = [IsAdminUser]

    @action(
        detail=False,
        methods=["POST"],
        url_path="start",
    )
    def start_chat(self, request: Request) -> Response:
        """
        Start a new image generation chat session.

        POST /api/v1/admin/identity-image-chat/start/

        Creates a new Gemini chat session for the specified user,
        replacing any existing session.

        Body (JSON):
            - identity_id: UUID of the identity (required)
            - user_id: UUID of the user (required)
            - additional_prompt: Extra instructions (optional)

        Returns: 200 OK with image_base64, identity_id, identity_name
        """
        serializer = StartImageChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return admin_start_image_chat(
            identity_id=str(serializer.validated_data["identity_id"]),
            user_id=str(serializer.validated_data["user_id"]),
            additional_prompt=serializer.validated_data.get("additional_prompt", ""),
        )

    @action(
        detail=False,
        methods=["POST"],
        url_path="continue",
    )
    def continue_chat(self, request: Request) -> Response:
        """
        Continue an existing image chat with an edit prompt.

        POST /api/v1/admin/identity-image-chat/continue/

        Loads the user's existing chat session and sends an edit request.

        Body (JSON):
            - user_id: UUID of the user (required)
            - edit_prompt: Edit instruction (required)

        Returns: 200 OK with image_base64, identity_id, identity_name
        Errors:
            - 400: No active chat, empty edit prompt
            - 404: User not found
            - 500: Image generation failed
        """
        serializer = ContinueImageChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return admin_continue_image_chat(
            user_id=str(serializer.validated_data["user_id"]),
            edit_prompt=serializer.validated_data["edit_prompt"],
        )
