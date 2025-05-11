from django.forms import model_to_dict
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

log = configure_logging(__name__, log_level="INFO")


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
        chat_history_for_prompt = (
            ChatMessage.objects.filter(user=request.user)
            .order_by("timestamp")[:5]
            .all()
        )
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
        large_chat_history = (
            ChatMessage.objects.filter(user=request.user)
            .order_by("timestamp")[:20]
            .all()
        )
        chat_history_serialized = ChatMessageSerializer(
            large_chat_history, many=True
        ).data

        # Step 8: Serialize all identities for the user
        from apps.identities.models import Identity

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
