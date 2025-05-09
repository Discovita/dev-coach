from django.forms import model_to_dict
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.request import Request
from apps.coach.serializers import CoachRequestSerializer, CoachResponseSerializer
from apps.coach_states.models import CoachState
from apps.coach_states.serializer import CoachStateSerializer
from apps.chat_messages.utils import add_chat_message
from enums.message_role import MessageRole
from models.CoachChatResponse import CoachChatResponse
from services.action_handler.handler import apply_actions
from rest_framework.decorators import action
from services.prompt_manager.manager import PromptManager
from services.ai import AIServiceFactory
from apps.chat_messages.models import ChatMessage
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


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
        # Parse and validate the incoming request
        serializer = CoachRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.validated_data["message"]
        model = serializer.get_model()

        # Add the user message to the chat history (async)
        add_chat_message(request.user, message, MessageRole.USER)

        # Retrieve the user's CoachState
        try:
            coach_state = CoachState.objects.get(user=request.user)
        except CoachState.DoesNotExist:
            return Response(
                {"detail": "Coach state not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Build the prompt using the PromptManager
        prompt_manager = PromptManager()
        coach_prompt, response_format = prompt_manager.create_chat_prompt(
            user=request.user, model=model
        )
        # Get the last 5 messages from the chat history
        chat_history = (
            ChatMessage.objects.filter(user=request.user)
            .order_by("-timestamp")[:5]
            .all()
        )
        ai_service = AIServiceFactory.create(model)

        response: CoachChatResponse = ai_service.generate(
            coach_prompt, chat_history, response_format, model
        )
        log.debug(f"AI response: {response}")
        log.debug(f"AI response: {type(response)}")
        # add the coach response to the chat history (async)
        add_chat_message(request.user, response.message, MessageRole.COACH)
        new_state, actions = apply_actions(coach_state, response)
        coach_state_serializer = CoachStateSerializer(new_state)

        response_data = {
            "message": response.message,
            "coach_state": coach_state_serializer.data,
            "final_prompt": coach_prompt,
            "actions": actions,
        }
        # Serialize the response
        serializer = CoachResponseSerializer(data=response_data)
        serializer.is_valid(raise_exception=True)
        if not serializer.is_valid():
            log.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)
