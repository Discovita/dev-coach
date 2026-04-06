"""
AdminTestUserViewSet for admin test scenario endpoints.

Provides admin-only endpoints that mirror the ``UserViewSet`` ``me/``
endpoints but operate on an arbitrary user identified by PK.

See: apps/users/views/__init__.py
"""

from django.shortcuts import get_object_or_404
from rest_framework import decorators, status, viewsets
from rest_framework.response import Response

from apps.chat_messages.utils import ensure_initial_message_exists
from apps.users.functions import get_user_chat_messages, get_user_identities
from apps.users.models import User
from permissions import IsAdminUser


class AdminTestUserViewSet(viewsets.GenericViewSet):
    """
    Admin-only ViewSet for test-scenario user endpoints.

    Every action requires ``IsAdminUser`` and looks up the target user
    via the ``pk`` URL parameter.
    """

    permission_classes = [IsAdminUser]

    @decorators.action(detail=False, methods=["get"], url_path="all")
    def list_all(self, request):
        """
        GET /api/v1/test-user/all — list all users with basic info.

        Used by admin impersonation UI to browse and select a user to view as.
        Returns lightweight user objects (no nested identities/messages).
        Includes test_scenario info so the UI can distinguish real vs test users.
        """
        from apps.coach_states.models import CoachState

        users = User.objects.select_related("test_scenario").all().order_by("-last_login")
        coach_states = {
            cs.user_id: cs.current_phase
            for cs in CoachState.objects.select_related("user").all()
        }
        data = []
        for u in users:
            scenario = getattr(u, "test_scenario", None)
            data.append(
                {
                    "id": str(u.id),
                    "email": u.email,
                    "first_name": u.first_name,
                    "last_name": u.last_name,
                    "is_active": u.is_active,
                    "is_staff": u.is_staff,
                    "is_superuser": u.is_superuser,
                    "last_login": u.last_login.isoformat() if u.last_login else None,
                    "created_at": u.date_joined.isoformat() if u.date_joined else None,
                    "coaching_phase": coach_states.get(u.id),
                    "is_test_user": scenario is not None,
                    "test_scenario_name": scenario.name if scenario else None,
                }
            )
        return Response(data)

    @decorators.action(detail=True, methods=["get"], url_path="profile")
    def get_profile(self, request, pk=None):
        """GET /api/v1/admin/test-user/{id}/profile — profile data for a test user."""
        from apps.users.serializers import UserProfileSerializer

        user = get_object_or_404(User, pk=pk)
        return Response(UserProfileSerializer(user).data)

    @decorators.action(detail=True, methods=["patch"], url_path="update-profile")
    def patch_profile(self, request, pk=None):
        """PATCH /api/v1/admin/test-user/{id}/update-profile — partial profile update."""
        from apps.users.serializers import UserProfileSerializer

        user = get_object_or_404(User, pk=pk)
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=True, methods=["get"], url_path="complete")
    def complete(self, request, pk=None):
        """GET /api/v1/admin/test-user/{id}/complete — full user data with initial message."""
        from apps.users.serializers import UserSerializer

        user = get_object_or_404(User, pk=pk)
        ensure_initial_message_exists(user)
        return Response(UserSerializer(user).data)

    @decorators.action(detail=True, methods=["get"], url_path="coach-state")
    def coach_state(self, request, pk=None):
        """GET /api/v1/admin/test-user/{id}/coach-state."""
        from apps.coach_states.models import CoachState
        from apps.coach_states.serializers import CoachStateSerializer

        user = get_object_or_404(User, pk=pk)
        coach_state = get_object_or_404(CoachState, user=user)
        return Response(CoachStateSerializer(coach_state).data)

    @decorators.action(detail=True, methods=["get"], url_path="identities")
    def identities(self, request, pk=None):
        """GET /api/v1/admin/test-user/{id}/identities — with archive filtering."""
        from apps.identities.serializers import IdentitySerializer

        user = get_object_or_404(User, pk=pk)
        include_archived = (
            request.query_params.get("include_archived", "false").lower() == "true"
        )
        archived_only = (
            request.query_params.get("archived_only", "false").lower() == "true"
        )
        identities = get_user_identities(
            user=user,
            include_archived=include_archived,
            archived_only=archived_only,
        )
        return Response(IdentitySerializer(identities, many=True).data)

    @decorators.action(detail=True, methods=["get"], url_path="actions")
    def actions(self, request, pk=None):
        """GET /api/v1/admin/test-user/{id}/actions."""
        from apps.actions.models import Action
        from apps.actions.serializers import ActionSerializer

        user = get_object_or_404(User, pk=pk)
        actions = Action.objects.filter(user=user).order_by("-timestamp")
        return Response(ActionSerializer(actions, many=True).data)

    @decorators.action(detail=True, methods=["get"], url_path="chat-messages")
    def chat_messages(self, request, pk=None):
        """GET /api/v1/admin/test-user/{id}/chat-messages — with initial message guarantee."""
        from apps.chat_messages.serializers import ChatMessageSerializer

        user = get_object_or_404(User, pk=pk)
        messages = get_user_chat_messages(user)
        return Response(ChatMessageSerializer(messages, many=True).data)
