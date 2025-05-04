from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.request import Request
from apps.coach.serializers import CoachRequestSerializer, CoachResponseSerializer
from apps.coach_states.models import CoachState
from services.action_handler.handler import apply_actions
# from your_openai_service import OpenAIService  # TODO: Implement or import your OpenAI service

# Create your views here.

class CoachUserInputView(APIView):
    """
    Handle user input and get coach response for the chatbot.
    Step-by-step:
    1. Require authentication (JWT or session)
    2. Parse and validate the incoming request (CoachRequestSerializer)
    3. Retrieve the user's CoachState from the database
    4. Build the prompt and call the OpenAI service (stub for now)
    5. Parse the LLM response (Pydantic model), extract actions
    6. Apply actions to update the CoachState and related models
    7. Return the response using CoachResponseSerializer
    """
    permission_classes = [IsAuthenticated]

    async def post(self, request: Request):
        # 1. Parse and validate the incoming request
        serializer = CoachRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.validated_data["message"]

        # 2. Retrieve the user's CoachState
        try:
            coach_state = await CoachState.objects.aget(user=request.user)
        except CoachState.DoesNotExist:
            return Response({"detail": "Coach state not found."}, status=status.HTTP_404_NOT_FOUND)

        # 3. Build the prompt and call the OpenAI service (stub for now)
        # TODO: Replace this stub with actual OpenAI service call
        # Example: result = await openai_service.process_message(message, coach_state)
        # For now, we'll mock a response:
        result = {
            "message": f"Echo: {message}",
            "coach_state": {},  # Should be the updated state as dict
            "final_prompt": "...",
            "actions": [],
        }

        # 4. Parse the LLM response and extract actions (stub: empty list)
        actions = result.get("actions", [])

        # 5. Apply actions to update the CoachState and related models
        apply_actions(coach_state, actions)

        # 6. Prepare the response
        response_data = {
            "message": result["message"],
            "coach_state": {},  # TODO: serialize the updated CoachState
            "final_prompt": result["final_prompt"],
            "actions": actions,
        }
        response_serializer = CoachResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
