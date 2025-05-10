from rest_framework import viewsets, decorators
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from apps.users.serializer import UserSerializer, UserProfileSerializer
from rest_framework.response import Response

from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


class UserViewSet(viewsets.GenericViewSet):
    """
    ViewSet for user related endpoints.
    """

    @decorators.action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="me",
    )
    def me(self, request: Request):
        """
        Get current user data.
        """
        return Response(UserProfileSerializer(request.user).data)

    @decorators.action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="me/complete",
    )
    def complete(self, request: Request):
        """
        Get current user data.
        """
        return Response(UserSerializer(request.user).data)

    @decorators.action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="me/coach-state",
    )
    def coach_state(self, request: Request):
        """
        Get the authenticated user's coach state.
        """
        from apps.coach_states.models import CoachState
        from apps.coach_states.serializer import CoachStateSerializer

        try:
            coach_state = CoachState.objects.get(user=request.user)
        except CoachState.DoesNotExist:
            return Response({"detail": "Coach state not found."}, status=404)
        return Response(CoachStateSerializer(coach_state).data)

    @decorators.action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="me/identities",
    )
    def identities(self, request: Request):
        """
        Get the authenticated user's identities.
        """
        from apps.identities.models import Identity
        from apps.identities.serializer import IdentitySerializer

        identities = Identity.objects.filter(user=request.user)
        return Response(IdentitySerializer(identities, many=True).data)

    @decorators.action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="me/chat-messages",
    )
    def chat_messages(self, request: Request):
        """
        Get the authenticated user's chat messages.
        If the chat history is empty, add the initial bot message and return it.
        """
        from apps.chat_messages.models import ChatMessage
        from apps.chat_messages.serializer import ChatMessageSerializer
        from apps.chat_messages.utils import get_initial_message, add_chat_message
        from enums.message_role import MessageRole

        chat_messages = ChatMessage.objects.filter(user=request.user).order_by(
            "-timestamp"
        )

        # If no messages exist, add the initial bot message
        if not chat_messages.exists():
            initial_message = get_initial_message()
            if initial_message:
                add_chat_message(request.user, initial_message, MessageRole.COACH)
                # Re-fetch chat messages after adding the initial message
                chat_messages = ChatMessage.objects.filter(user=request.user).order_by(
                    "-timestamp"
                )

        return Response(ChatMessageSerializer(chat_messages, many=True).data)
