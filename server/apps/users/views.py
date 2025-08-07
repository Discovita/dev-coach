from rest_framework import viewsets, decorators
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from apps.users.serializer import UserSerializer, UserProfileSerializer
from rest_framework.response import Response

from enums.identity_category import IdentityCategory
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
        Get current user data, ensuring the chat history contains the initial bot message if empty.
        """
        from apps.chat_messages.models import ChatMessage
        from apps.chat_messages.utils import get_initial_message, add_chat_message
        from enums.message_role import MessageRole

        chat_messages = ChatMessage.objects.filter(user=request.user)
        if not chat_messages.exists():
            initial_message = get_initial_message()
            if initial_message:
                add_chat_message(request.user, initial_message, MessageRole.COACH)
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
        from apps.chat_messages.models import ChatMessage
        from apps.chat_messages.serializer import ChatMessageSerializer
        from apps.chat_messages.utils import get_initial_message, add_chat_message
        from enums.message_role import MessageRole

        chat_messages_qs = ChatMessage.objects.filter(user=request.user).order_by(
            "-timestamp"
        )

        if not chat_messages_qs.exists():
            initial_message = get_initial_message()
            if initial_message:
                add_chat_message(request.user, initial_message, MessageRole.COACH)
                chat_messages_qs = ChatMessage.objects.filter(
                    user=request.user
                ).order_by("-timestamp")

        latest_messages_qs = chat_messages_qs[:20]
        ordered_messages = list(reversed(latest_messages_qs))

        return Response(ChatMessageSerializer(ordered_messages, many=True).data)

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
        from apps.chat_messages.models import ChatMessage
        from apps.chat_messages.serializer import ChatMessageSerializer
        from apps.chat_messages.utils import get_initial_message, add_chat_message
        from enums.message_role import MessageRole
        from apps.coach_states.models import CoachState
        from enums.coaching_phase import CoachingPhase
        from apps.identities.models import Identity
        from apps.user_notes.models import UserNote
        from apps.actions.models import Action

        # Delete all chat messages for the user
        ChatMessage.objects.filter(user=request.user).delete()

        # Delete all identities for the user
        Identity.objects.filter(user=request.user).delete()

        # Delete all user notes for the user
        UserNote.objects.filter(user=request.user).delete()

        # Delete all actions for the user
        Action.objects.filter(user=request.user).delete()

        # Reset the user's CoachState
        try:
            coach_state = CoachState.objects.get(user=request.user)
            coach_state.current_phase = CoachingPhase.INTRODUCTION
            coach_state.current_identity = None
            coach_state.proposed_identity = None
            coach_state.identity_focus = IdentityCategory.PASSIONS
            coach_state.skipped_identity_categories = []
            coach_state.who_you_are = []
            coach_state.who_you_want_to_be = []
            coach_state.save()
        except CoachState.DoesNotExist:
            pass  # Optionally, handle if the user does not have a CoachState

        # Add the initial bot message (if any)
        initial_message = get_initial_message()
        if initial_message:
            add_chat_message(request.user, initial_message, MessageRole.COACH)

        # Return the new chat history
        chat_messages = ChatMessage.objects.filter(user=request.user).order_by(
            "-timestamp"
        )
        return Response(ChatMessageSerializer(chat_messages, many=True).data)


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
    def profile(self, request, pk=None):
        """
        Get profile data for a test scenario user.
        """
        if not self.admin_required(request):
            return Response({"detail": "Not authorized."}, status=403)
        user = self.get_test_user(pk)
        if not user:
            return Response({"detail": "User not found."}, status=404)
        from apps.users.serializer import UserProfileSerializer

        return Response(UserProfileSerializer(user).data)

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
        from apps.chat_messages.models import ChatMessage
        from apps.chat_messages.utils import get_initial_message, add_chat_message
        from enums.message_role import MessageRole

        chat_messages = ChatMessage.objects.filter(user=user)
        if not chat_messages.exists():
            initial_message = get_initial_message()
            if initial_message:
                add_chat_message(user, initial_message, MessageRole.COACH)
        from apps.users.serializer import UserSerializer

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
        """
        if not self.admin_required(request):
            return Response({"detail": "Not authorized."}, status=403)
        user = self.get_test_user(pk)
        if not user:
            return Response({"detail": "User not found."}, status=404)
        from apps.identities.models import Identity
        from apps.identities.serializer import IdentitySerializer

        identities = Identity.objects.filter(user=user)
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
        from apps.chat_messages.models import ChatMessage
        from apps.chat_messages.serializer import ChatMessageSerializer
        from apps.chat_messages.utils import get_initial_message, add_chat_message
        from enums.message_role import MessageRole

        chat_messages_qs = ChatMessage.objects.filter(user=user).order_by("-timestamp")
        if not chat_messages_qs.exists():
            initial_message = get_initial_message()
            if initial_message:
                add_chat_message(user, initial_message, MessageRole.COACH)
                chat_messages_qs = ChatMessage.objects.filter(user=user).order_by(
                    "-timestamp"
                )
        latest_messages_qs = chat_messages_qs
        ordered_messages = list(reversed(latest_messages_qs))
        return Response(ChatMessageSerializer(ordered_messages, many=True).data)
