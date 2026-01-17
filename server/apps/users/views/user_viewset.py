"""
UserViewSet for authenticated user endpoints.

This module contains the viewset for user-related endpoints where the authenticated
user accesses their own data (me/ endpoints).
"""

from rest_framework import viewsets, decorators
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.serializers import UserSerializer, UserProfileSerializer
from apps.users.functions import (
    get_user_identities,
    get_user_chat_messages,
    reset_user_coaching_data,
)
from apps.users.utils import ensure_initial_message_exists
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


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
        Get current user data, ensuring the chat history contains the initial bot message if empty.
        """
        ensure_initial_message_exists(request.user)
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
        Query parameters:
        - include_archived=true: Include archived identities
        - archived_only=true: Return only archived identities
        By default, excludes archived identities.
        """
        from apps.identities.serializer import IdentitySerializer

        log.debug(f"Identities Request: {request.user}")

        include_archived = request.query_params.get('include_archived', 'false').lower() == 'true'
        archived_only = request.query_params.get('archived_only', 'false').lower() == 'true'

        identities = get_user_identities(
            user=request.user,
            include_archived=include_archived,
            archived_only=archived_only,
        )

        response = IdentitySerializer(identities, many=True).data
        log.debug(f"Identities Response: {response}")
        return Response(response)

    @decorators.action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="me/actions",
    )
    def actions(self, request: Request):
        """
        Get the authenticated user's actions.
        """
        from apps.actions.models import Action
        from apps.actions.serializer import ActionSerializer

        actions = Action.objects.filter(user=request.user).order_by("-timestamp")
        return Response(ActionSerializer(actions, many=True).data)

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
        from apps.chat_messages.serializer import ChatMessageSerializer

        messages = get_user_chat_messages(request.user)
        return Response(ChatMessageSerializer(messages, many=True).data)

    @decorators.action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="me/reset-chat-messages",
    )
    def reset_chat_messages(self, request: Request):
        """
        Reset (delete) all chat messages, identities, and user notes for the authenticated user, and reset their CoachState.
        """
        from apps.chat_messages.serializer import ChatMessageSerializer

        messages = reset_user_coaching_data(request.user)
        return Response(ChatMessageSerializer(messages, many=True).data)

    @decorators.action(
        detail=False,
        methods=["patch"],
        permission_classes=[IsAuthenticated],
        url_path="me",
    )
    def update_me(self, request: Request):
        """
        Update the authenticated user's profile data (partial update).
        PATCH /api/v1/user/me/
        Body: Partial user data (see UserProfileSerializer)
        Returns: 200 OK, updated user profile object.
        """
        from rest_framework import status

        serializer = UserProfileSerializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
