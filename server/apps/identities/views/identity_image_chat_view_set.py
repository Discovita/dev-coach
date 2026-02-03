"""
Identity Image Chat ViewSet

User-facing endpoints for image generation chat sessions.
Uses the authenticated user - no user_id parameter needed.
"""

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.request import Request

from apps.identities.serializers import (
    StartImageChatRequestSerializer,
    ContinueImageChatRequestSerializer,
)
from apps.identities.functions.public import (
    start_image_chat,
    continue_image_chat,
)
from services.logger import configure_logging

log = configure_logging(__name__)


class IdentityImageChatViewSet(viewsets.GenericViewSet):
    """
    User-facing endpoints for identity image generation.

    Endpoints:
    - POST /api/v1/identity-image-chat/start/   → start_chat()
    - POST /api/v1/identity-image-chat/continue/ → continue_chat()
    """

    permission_classes = [IsAuthenticated]

    @action(
        detail=False,
        methods=["POST"],
        url_path="start",
    )
    def start_chat(self, request: Request) -> Response:
        """
        Start a new image generation chat session.

        POST /api/v1/identity-image-chat/start/

        Creates a new Gemini chat session for the authenticated user,
        replacing any existing session.

        Body (JSON):
            - identity_id: UUID of the identity (required)
            - additional_prompt: Extra instructions (optional)

        Returns: 200 OK with image_base64, identity_id, identity_name
        """
        serializer = StartImageChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return start_image_chat(
            user=request.user,
            identity_id=str(serializer.validated_data["identity_id"]),
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

        POST /api/v1/identity-image-chat/continue/

        Loads the authenticated user's existing chat session
        and sends an edit request.

        Body (JSON):
            - edit_prompt: Edit instruction (required)

        Returns: 200 OK with image_base64, identity_id, identity_name
        Errors:
            - 400: No active chat, empty edit prompt
            - 500: Image generation failed
        """
        serializer = ContinueImageChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return continue_image_chat(
            user=request.user,
            edit_prompt=serializer.validated_data["edit_prompt"],
        )
