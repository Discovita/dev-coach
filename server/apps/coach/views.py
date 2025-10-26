from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.request import Request
from apps.coach.serializers import CoachRequestSerializer, CoachResponseSerializer
from apps.coach_states.models import CoachState
from apps.chat_messages.utils import add_chat_message, get_initial_message
from enums.message_role import MessageRole
from models.CoachChatResponse import CoachChatResponse
from services.action_handler.handler import apply_coach_actions, apply_component_actions
from models.components.ComponentConfig import ComponentAction
from rest_framework.decorators import action
from services.prompt_manager.manager import PromptManager
from services.ai import AIServiceFactory
from apps.chat_messages.models import ChatMessage
from django.contrib.auth import get_user_model
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")

"""
Admin Impersonation – Current Implementation Overview
----------------------------------------------------

Scope:
    The system supports admin-only impersonation via a dedicated endpoint, not by adding
    impersonation parameters to general user endpoints.

Notes:
    - Component actions in the admin endpoint are applied to the acting user's CoachState,
      with the admin user passed as the executor/auditor.
    - All access and impersonation attempts are logged for auditability.

Security:
    - Only admins may use impersonation.
    - Requests without a valid 'user_id' or with a non-existent user are rejected.
"""


class CoachViewSet(
    viewsets.GenericViewSet,
):
    """Endpoints for processing coach messages, including admin impersonation."""

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"], url_path="process-message")
    def process_message(self, request: Request):
        """
        Process a message for the authenticated user.

        Behavior:
            - Ensure initial coach message for the user if chat is empty.
            - Add the provided user message to the user's chat history.
            - Retrieve the user's CoachState.
            - Apply component actions (if provided) to the user's CoachState.
            - Build prompt (PromptManager) and fetch the user's last 5 chat messages.
            - Generate response (AIServiceFactory).
            - Add coach response to the user's chat history.
            - Apply coach actions; may include component configuration.
            - Serialize and return.

        Response:
            - CoachResponseSerializer with:
                - 'message' (str)
                - 'final_prompt' (str)
                - 'component' (object) optional
        """
        serializer = CoachRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.validated_data["message"]
        request_component_actions = serializer.validated_data.get("actions", [])
        model = serializer.get_model()

        chat_history_qs = ChatMessage.objects.filter(user=request.user)
        if not chat_history_qs.exists():
            initial_message = get_initial_message()
            if initial_message:
                add_chat_message(request.user, initial_message, MessageRole.COACH)

        user_chat_message = add_chat_message(request.user, message, MessageRole.USER)

        # NOTE: CoachState is guaranteed to exist because we use Django Signals to create one when a user is created
        # see apps.coach_states.signals.py
        coach_state = CoachState.objects.get(user=request.user)

        if request_component_actions:
            component_actions = [
                ComponentAction(**action) if isinstance(action, dict) else action
                for action in request_component_actions
            ]
            apply_component_actions(coach_state, component_actions, user_chat_message)

        prompt_manager = PromptManager()

        coach_prompt, response_format = prompt_manager.create_chat_prompt(
            user=request.user, model=model
        )

        chat_history_for_prompt_query_set = ChatMessage.objects.filter(
            user=request.user
        ).order_by("-timestamp")[:5]

        chat_history_for_prompt = list(reversed(chat_history_for_prompt_query_set))

        ai_service = AIServiceFactory.create(model)

        response: CoachChatResponse = ai_service.generate(
            coach_prompt, chat_history_for_prompt, response_format, model
        )

        coach_message = add_chat_message(
            request.user, response.message, MessageRole.COACH
        )

        new_state, component_config = apply_coach_actions(
            coach_state, response, coach_message
        )

        log.debug(f"New State: {new_state}")
        log.debug(f"Component Config: {component_config}")

        response_data = {
            "message": response.message,
            "final_prompt": coach_prompt,
        }

        if component_config:
            response_data["component"] = component_config.model_dump()

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

        Behavior:
            - Ensure initial coach message for the acting user if chat is empty.
            - Add the provided message to the acting user's chat history.
            - Retrieve the acting user's CoachState.
            - Apply component actions (if provided) to the acting user's CoachState (admin as executor).
            - Build prompt (PromptManager) and fetch the acting user's last 5 chat messages.
            - Generate response (AIServiceFactory).
            - Add coach response to the acting user's chat history.
            - Apply coach actions; may include component configuration.
            - Serialize and return.

        Response:
            - CoachResponseSerializer with:
                - 'message' (str)
                - 'final_prompt' (str)
                - 'component' (object) optional
        """
        log.info(f"Processing Request: {request.data}")
        try:
            log.info(
                f"Request user: {request.user} (is_staff: {request.user.is_staff}, is_superuser: {request.user.is_superuser})"
            )

            if not request.user.is_staff and not request.user.is_superuser:
                log.warning(f"Unauthorized access attempt by user {request.user}")
                return Response({"detail": "Not authorized."}, status=403)

            serializer = CoachRequestSerializer(data=request.data)
            if not serializer.is_valid():
                log.error(f"Serializer validation failed: {serializer.errors}")
                return Response(
                    {"detail": "Invalid request data.", "errors": serializer.errors},
                    status=400,
                )

            user_id = serializer.validated_data.get("user_id")
            # user_id not required in the serializer, but it is required in this endpoint
            if not user_id:
                log.error("user_id is missing from request")
                return Response({"detail": "user_id is required."}, status=400)
            message = serializer.validated_data["message"]
            request_component_actions = serializer.validated_data.get("actions", [])
            model = serializer.get_model()

            User = get_user_model()
            # try/except block here because the admin may have passed in a user_id that doesn't exist
            # TODO: The validation for the user_id should be moved to the serializer
            try:
                acting_user = User.objects.get(pk=user_id)
                log.info(f"Found acting user: {acting_user}")
            except User.DoesNotExist:
                log.error(f"User with id {user_id} not found")
                return Response(
                    {"detail": f"User with id {user_id} not found."}, status=404
                )

            # Get the acting user's chat history. If it doesn't exist, create it with the initial message
            chat_history_qs = ChatMessage.objects.filter(user=acting_user)
            if not chat_history_qs.exists():
                initial_message = get_initial_message()
                if initial_message:
                    add_chat_message(acting_user, initial_message, MessageRole.COACH)

            acting_user_chat_message = add_chat_message(
                acting_user, message, MessageRole.USER
            )

            # NOTE: CoachState is guaranteed to exist because we use Django Signals to create one when a user is created
            # see apps.coach_states.signals.py
            coach_state = CoachState.objects.get(user=acting_user)

            if request_component_actions:
                component_actions = [
                    ComponentAction(**action) if isinstance(action, dict) else action
                    for action in request_component_actions
                ]
                apply_component_actions(
                    coach_state, component_actions, acting_user_chat_message
                )

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

            coach_message = add_chat_message(
                acting_user, response.message, MessageRole.COACH
            )

            new_state, component_config = apply_coach_actions(
                coach_state, response, coach_message
            )

            log.debug(f"New State: {new_state}")
            log.debug(f"Component Config: {component_config}")

            response_data = {
                "message": response.message,
                "final_prompt": coach_prompt,
            }

            if component_config:
                response_data["component"] = component_config.model_dump()

            serializer = CoachResponseSerializer(data=response_data)
            serializer.is_valid(raise_exception=True)
            if not serializer.is_valid():
                log.error(f"Serializer errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            log.error(
                f"Unexpected error in process_message_for_user: {str(e)}", exc_info=True
            )
            return Response({"detail": f"Internal server error: {str(e)}"}, status=500)
