from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.request import Request
from apps.coach.serializers import CoachRequestSerializer, CoachResponseSerializer
from apps.coach_states.models import CoachState
from apps.chat_messages.utils import add_chat_message_async
from enums.message_role import MessageRole
from services.action_handler.handler import apply_actions
from services.prompt_manager.manager import PromptManager
from services.ai import AIServiceFactory
from apps.chat_messages.models import ChatMessage


class CoachView(APIView):
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

    async def post(self, request: Request):
        # Parse and validate the incoming request
        serializer = CoachRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.validated_data["message"]
        model = serializer.get_model()

        # Add the user message to the chat history (async)
        await add_chat_message_async(request.user, message, MessageRole.USER)

        # Retrieve the user's CoachState
        try:
            coach_state = await CoachState.objects.aget(user=request.user)
        except CoachState.DoesNotExist:
            return Response(
                {"detail": "Coach state not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Build the prompt using the PromptManager
        prompt_manager = PromptManager()
        coach_prompt, response_format = await prompt_manager.create_chat_prompt(
            user=request.user, model=model
        )
        # Get the last 5 messages from the chat history
        chat_history = (
            await ChatMessage.objects.filter(user=request.user)
            .order_by("-timestamp")[:5]
            .aall()
        )
        ai_service = AIServiceFactory.create(model)

        response = await ai_service.generate(
            coach_prompt, chat_history, response_format, model
        )
        # add the coach response to the chat history (async)
        await add_chat_message_async(request.user, response.message, MessageRole.COACH)
        new_state = apply_actions(coach_state, response.actions)

        response_data = {
            "message": response.message,
            "state": new_state,
            "actions": response.,
        }
        # Serialize the response
        serializer = CoachResponseSerializer(data=response_data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
