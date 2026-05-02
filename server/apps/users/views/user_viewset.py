"""
UserViewSet for authenticated user endpoints.

Provides ``me/`` endpoints where the authenticated user accesses their own
data (profile, coach state, identities, chat messages, etc.).

See: apps/users/views/__init__.py
"""

from django.shortcuts import get_object_or_404
from rest_framework import decorators, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.chat_messages.utils import ensure_initial_message_exists
from apps.users.functions import (
    get_user_chat_messages,
    get_user_identities,
    reset_user_coaching_data,
)
from apps.users.serializers import UserProfileSerializer, UserSerializer


class UserViewSet(viewsets.GenericViewSet):
    """
    Authenticated-user ViewSet for ``me/`` endpoints.

    All actions operate on ``request.user`` — no PK is needed.
    """

    @decorators.action(
        detail=False,
        methods=["get", "patch"],
        permission_classes=[IsAuthenticated],
        url_path="me",
    )
    def me(self, request: Request):
        """
        GET  /api/v1/user/me/ — current user profile.
        PATCH /api/v1/user/me/ — partial profile update.
        """
        if request.method == "PATCH":
            serializer = UserProfileSerializer(
                request.user, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(UserProfileSerializer(request.user).data)

    @decorators.action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="me/complete",
    )
    def complete(self, request: Request):
        """GET /api/v1/user/me/complete — full user data with initial message guarantee."""
        ensure_initial_message_exists(request.user)
        return Response(UserSerializer(request.user).data)

    @decorators.action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="me/coach-state",
    )
    def coach_state(self, request: Request):
        """GET /api/v1/user/me/coach-state."""
        from apps.coach_states.models import CoachState
        from apps.coach_states.serializers import CoachStateSerializer

        coach_state = get_object_or_404(CoachState, user=request.user)
        return Response(CoachStateSerializer(coach_state).data)

    @decorators.action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="me/identities",
    )
    def identities(self, request: Request):
        """
        GET /api/v1/user/me/identities — with archive filtering.

        Query params: ``include_archived``, ``archived_only`` (default ``false``).
        """
        from apps.identities.serializers import IdentitySerializer

        include_archived = (
            request.query_params.get("include_archived", "false").lower() == "true"
        )
        archived_only = (
            request.query_params.get("archived_only", "false").lower() == "true"
        )
        identities = get_user_identities(
            user=request.user,
            include_archived=include_archived,
            archived_only=archived_only,
        )
        return Response(IdentitySerializer(identities, many=True).data)

    @decorators.action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="me/actions",
    )
    def actions(self, request: Request):
        """GET /api/v1/user/me/actions."""
        from apps.actions.models import Action
        from apps.actions.serializers import ActionSerializer

        actions = Action.objects.filter(user=request.user).order_by("-timestamp")
        return Response(ActionSerializer(actions, many=True).data)

    @decorators.action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="me/chat-messages",
    )
    def chat_messages(self, request: Request):
        """GET /api/v1/user/me/chat-messages — with initial message guarantee."""
        from apps.chat_messages.serializers import ChatMessageSerializer

        messages = get_user_chat_messages(request.user)
        return Response(ChatMessageSerializer(messages, many=True).data)

    @decorators.action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="me/reset-chat-messages",
    )
    def reset_chat_messages(self, request: Request):
        """POST /api/v1/user/me/reset-chat-messages — reset all coaching data."""
        from apps.chat_messages.serializers import ChatMessageSerializer

        messages = reset_user_coaching_data(request.user)
        return Response(ChatMessageSerializer(messages, many=True).data)
