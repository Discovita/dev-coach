"""
TestUserViewSet for admin test scenario endpoints.

This module contains the viewset for test scenario user-related endpoints
where admin users can access and manage test user data.
"""

from rest_framework import viewsets, decorators
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.functions import get_user_identities, get_user_chat_messages
from apps.users.utils import ensure_initial_message_exists


class TestUserViewSet(viewsets.GenericViewSet):
    """
    ViewSet for test scenario user related endpoints.
    All endpoints require admin/superuser and a user id (pk).
    """

    def get_test_user(self, pk):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def admin_required(self, request):
        return request.user.is_staff or request.user.is_superuser

    @decorators.action(
        detail=True,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="profile",
    )
    def get_profile(self, request, pk=None):
        """
        Get profile data for a test scenario user.
        GET /api/v1/test-user/{id}/profile
        """
        from apps.users.serializers import UserProfileSerializer

        if not self.admin_required(request):
            return Response({"detail": "Not authorized."}, status=403)
        user = self.get_test_user(pk)
        if not user:
            return Response({"detail": "User not found."}, status=404)

        return Response(UserProfileSerializer(user).data)

    @decorators.action(
        detail=True,
        methods=["patch"],
        permission_classes=[IsAuthenticated],
        url_path="update-profile",
    )
    def patch_profile(self, request, pk=None):
        """
        Update profile data for a test scenario user (admin only, partial update).
        PATCH /api/v1/test-user/{id}/update-profile
        Body: Partial user data (see UserProfileSerializer)
        Returns: 200 OK, updated user profile object.
        """
        from rest_framework import status
        from apps.users.serializers import UserProfileSerializer

        if not self.admin_required(request):
            return Response({"detail": "Not authorized."}, status=403)
        user = self.get_test_user(pk)
        if not user:
            return Response({"detail": "User not found."}, status=404)

        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(
        detail=True,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="complete",
    )
    def complete(self, request, pk=None):
        """
        Get complete data for a test scenario user, ensuring the chat history contains the initial bot message if empty.
        """
        if not self.admin_required(request):
            return Response({"detail": "Not authorized."}, status=403)
        user = self.get_test_user(pk)
        if not user:
            return Response({"detail": "User not found."}, status=404)
        from apps.users.serializers import UserSerializer

        ensure_initial_message_exists(user)
        return Response(UserSerializer(user).data)

    @decorators.action(
        detail=True,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="coach-state",
    )
    def coach_state(self, request, pk=None):
        """
        Get the coach state for a test scenario user.
        """
        if not self.admin_required(request):
            return Response({"detail": "Not authorized."}, status=403)
        user = self.get_test_user(pk)
        if not user:
            return Response({"detail": "User not found."}, status=404)
        from apps.coach_states.models import CoachState
        from apps.coach_states.serializer import CoachStateSerializer

        try:
            coach_state = CoachState.objects.get(user=user)
        except CoachState.DoesNotExist:
            return Response({"detail": "Coach state not found."}, status=404)
        return Response(CoachStateSerializer(coach_state).data)

    @decorators.action(
        detail=True,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="identities",
    )
    def identities(self, request, pk=None):
        """
        Get the identities for a test scenario user.
        Query parameters:
        - include_archived=true: Include archived identities
        - archived_only=true: Return only archived identities
        By default, excludes archived identities.
        """
        if not self.admin_required(request):
            return Response({"detail": "Not authorized."}, status=403)
        user = self.get_test_user(pk)
        if not user:
            return Response({"detail": "User not found."}, status=404)
        from apps.identities.serializer import IdentitySerializer

        include_archived = request.query_params.get('include_archived', 'false').lower() == 'true'
        archived_only = request.query_params.get('archived_only', 'false').lower() == 'true'

        identities = get_user_identities(
            user=user,
            include_archived=include_archived,
            archived_only=archived_only,
        )

        return Response(IdentitySerializer(identities, many=True).data)

    @decorators.action(
        detail=True,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="actions",
    )
    def actions(self, request, pk=None):
        """
        Get the actions for a test scenario user.
        """
        if not self.admin_required(request):
            return Response({"detail": "Not authorized."}, status=403)
        user = self.get_test_user(pk)
        if not user:
            return Response({"detail": "User not found."}, status=404)
        from apps.actions.models import Action
        from apps.actions.serializer import ActionSerializer

        actions = Action.objects.filter(user=user).order_by("-timestamp")
        return Response(ActionSerializer(actions, many=True).data)

    @decorators.action(
        detail=True,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="chat-messages",
    )
    def chat_messages(self, request, pk=None):
        """
        Get the chat messages for a test scenario user.
        If the chat history is empty, add the initial bot message and return it.
        """
        if not self.admin_required(request):
            return Response({"detail": "Not authorized."}, status=403)
        user = self.get_test_user(pk)
        if not user:
            return Response({"detail": "User not found."}, status=404)
        from apps.chat_messages.serializer import ChatMessageSerializer

        messages = get_user_chat_messages(user)
        return Response(ChatMessageSerializer(messages, many=True).data)

