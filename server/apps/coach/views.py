from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.request import Request
from apps.coach.serializers import CoachRequestSerializer, CoachResponseSerializer
from apps.coach_states.models import CoachState
from apps.coach_states.serializer import CoachStateSerializer
from apps.chat_messages.utils import add_chat_message, get_initial_message
from enums.message_role import MessageRole
from models.CoachChatResponse import CoachChatResponse
from services.action_handler.handler import apply_actions
from rest_framework.decorators import action
from services.prompt_manager.manager import PromptManager
from services.ai import AIServiceFactory
from apps.chat_messages.models import ChatMessage
from services.logger import configure_logging
from apps.chat_messages.serializer import ChatMessageSerializer
from apps.identities.serializer import IdentitySerializer
from apps.identities.models import Identity

log = configure_logging(__name__, log_level="INFO")

"""
Admin Impersonation Pattern for Test Scenarios
---------------------------------------------

Purpose:
    Allow admin users to simulate/test chatbot flows as a test user (from a TestScenario), even though the admin is the one authenticated.
    This is essential for running scenario-based tests and debugging without manual user switching.

Problem:
    By default, all endpoints use `request.user` for actions (creating messages, identities, etc.).
    When an admin is logged in, this would associate all new data with the admin, not the test user from the scenario.

Solution (Impersonation Pattern):
    - Allow admin users to specify a `user_id` or `test_scenario_id` in the request body.
    - If the requester is an admin (`is_staff` or `is_superuser`), use the specified test user for all downstream actions (instead of `request.user`).
    - Otherwise, default to `request.user`.
    - This enables admins to "impersonate" a test user for the duration of the request, ensuring all created/modified data is associated with the correct test user and scenario.

Implementation:
    1. In each relevant view (e.g., process_message), determine the acting user:
        acting_user = request.user
        if request.user.is_staff:
            if 'user_id' in request.data:
                acting_user = User.objects.get(id=request.data['user_id'])
            elif 'test_scenario_id' in request.data:
                scenario = TestScenario.objects.get(id=request.data['test_scenario_id'])
                acting_user = User.objects.get(test_scenario=scenario)
    2. Use `acting_user` everywhere instead of `request.user` for all business logic and object creation.
    3. Only allow this override for admin users (never for regular users).
    4. Log all impersonation actions for auditability.

Security Considerations:
    - Only trusted admin users should be able to impersonate others.
    - Always check permissions before allowing impersonation.
    - Consider logging impersonation events for traceability.

Benefits:
    - Enables robust scenario-based testing and debugging.
    - Prevents accidental data pollution by associating test data with the correct user/scenario.
    - Makes it easy to automate or manually test any phase of the chatbot flow.
"""


class CoachViewSet(
    viewsets.GenericViewSet,
):
    """
    Handle user input and get coach response for the chatbot.
    Step-by-step:
    1. Require authentication (JWT or session)
    2. Parse and validate the incoming request (CoachRequestSerializer)
    3. Retrieve the user's CoachState from the database
    4. Build the prompt and call the OpenAI service
    5. Parse the LLM response (Pydantic model), extract actions
    6. Apply actions to update the CoachState and related models
    7. Return the response using CoachResponseSerializer
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"], url_path="process-message")
    def process_message(self, request: Request):
        # Step 1: Parse and validate the incoming request
        serializer = CoachRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.validated_data["message"]
        model = serializer.get_model()

        # Step 2: Ensure chat history starts with the initial bot message if empty
        chat_history_qs = ChatMessage.objects.filter(user=request.user)
        if not chat_history_qs.exists():
            initial_message = get_initial_message()
            if initial_message:
                add_chat_message(request.user, initial_message, MessageRole.COACH)

        # Step 3: Add the user message to the chat history (async)
        add_chat_message(request.user, message, MessageRole.USER)

        # Step 4: Retrieve the user's CoachState
        try:
            coach_state = CoachState.objects.get(user=request.user)
        except CoachState.DoesNotExist:
            return Response(
                {"detail": "Coach state not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Step 5: Build the prompt using the PromptManager
        prompt_manager = PromptManager()
        coach_prompt, response_format = prompt_manager.create_chat_prompt(
            user=request.user, model=model
        )
        # Get the last 5 messages from the chat history
        chat_history_for_prompt_query_set = ChatMessage.objects.filter(
            user=request.user
        ).order_by("-timestamp")[
            :5
        ]  # Get the 5 newest messages
        # Convert queryset to list in chronological order (oldest to newest)
        chat_history_for_prompt = list(reversed(chat_history_for_prompt_query_set))

        ai_service = AIServiceFactory.create(model)

        response: CoachChatResponse = ai_service.generate(
            coach_prompt, chat_history_for_prompt, response_format, model
        )
        # Step 6: Add the coach response to the chat history (async)
        add_chat_message(request.user, response.message, MessageRole.COACH)
        new_state, actions = apply_actions(coach_state, response)
        coach_state_serializer = CoachStateSerializer(new_state)
        log.debug(f"Actions: {actions}")

        # Step 7: Serialize the latest chat history (last 20 messages)
        large_chat_history_query_set = ChatMessage.objects.filter(
            user=request.user
        ).order_by("-timestamp")
        # Convert queryset to list in chronological order
        large_chat_history = list(reversed(large_chat_history_query_set))
        chat_history_serialized = ChatMessageSerializer(
            large_chat_history, many=True
        ).data

        # Step 8: Serialize all identities for the user
        identities = Identity.objects.filter(user=request.user)
        identities_serialized = IdentitySerializer(identities, many=True).data

        response_data = {
            "message": response.message,
            "coach_state": coach_state_serializer.data,
            "final_prompt": coach_prompt,
            "actions": actions,
            "chat_history": chat_history_serialized,
            "identities": identities_serialized,
        }
        # Step 9: Serialize the response
        serializer = CoachResponseSerializer(data=response_data)
        serializer.is_valid(raise_exception=True)
        if not serializer.is_valid():
            log.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="process-message-for-user")
    def process_message_for_user(self, request: Request):
        """
        Process a message as if sent by a specific user (admin only).
        """
        if not request.user.is_staff and not request.user.is_superuser:
            return Response({"detail": "Not authorized."}, status=403)
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"detail": "user_id is required."}, status=400)
        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            acting_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)

        # Step 1: Parse and validate the incoming request
        serializer = CoachRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.validated_data["message"]
        model = serializer.get_model()

        # Step 2: Ensure chat history starts with the initial bot message if empty
        chat_history_qs = ChatMessage.objects.filter(user=acting_user)
        if not chat_history_qs.exists():
            initial_message = get_initial_message()
            if initial_message:
                add_chat_message(acting_user, initial_message, MessageRole.COACH)

        # Step 3: Add the user message to the chat history (async)
        add_chat_message(acting_user, message, MessageRole.USER)

        # Step 4: Retrieve the user's CoachState
        try:
            coach_state = CoachState.objects.get(user=acting_user)
        except CoachState.DoesNotExist:
            return Response(
                {"detail": "Coach state not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Step 5: Build the prompt using the PromptManager
        prompt_manager = PromptManager()
        coach_prompt, response_format = prompt_manager.create_chat_prompt(
            user=acting_user, model=model
        )
        chat_history_for_prompt_query_set = ChatMessage.objects.filter(
            user=acting_user
        ).order_by("-timestamp")[:5]
        chat_history_for_prompt = list(reversed(chat_history_for_prompt_query_set))

        ai_service = AIServiceFactory.create(model)
        response: CoachChatResponse = ai_service.generate(
            coach_prompt, chat_history_for_prompt, response_format, model
        )
        add_chat_message(acting_user, response.message, MessageRole.COACH)
        new_state, actions = apply_actions(coach_state, response)
        coach_state_serializer = CoachStateSerializer(new_state)
        log.debug(f"Actions: {actions}")

        large_chat_history_query_set = ChatMessage.objects.filter(
            user=acting_user
        ).order_by("-timestamp")[:20]
        large_chat_history = list(reversed(large_chat_history_query_set))
        chat_history_serialized = ChatMessageSerializer(
            large_chat_history, many=True
        ).data

        identities = Identity.objects.filter(user=acting_user)
        identities_serialized = IdentitySerializer(identities, many=True).data

        response_data = {
            "message": response.message,
            "coach_state": coach_state_serializer.data,
            "final_prompt": coach_prompt,
            "actions": actions,
            "chat_history": chat_history_serialized,
            "identities": identities_serialized,
        }
        serializer = CoachResponseSerializer(data=response_data)
        if not serializer.is_valid():
            log.error(f"Serializer errors: {serializer.errors}")
            log.error(f"Coach state serializer data: {coach_state_serializer.data}")
            log.error(
                f"Coach state serializer data type: {type(coach_state_serializer.data)}"
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)
