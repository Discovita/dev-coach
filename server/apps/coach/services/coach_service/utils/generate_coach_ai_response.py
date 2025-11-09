"""
Utility to generate the coach's response using AI.

This takes the prompt and conversation history and sends it to the AI service
to generate a personalized response from the coach.
"""
from apps.chat_messages.models import ChatMessage
from enums.ai import AIModel
from models.CoachChatResponse import CoachChatResponse
from pydantic import BaseModel
from services.ai import AIServiceFactory


def generate_coach_ai_response(
    coach_prompt: str,
    chat_history: list[ChatMessage],
    response_format: type[BaseModel],
    model: AIModel,
) -> CoachChatResponse:
    """
    Generate the coach's response using the AI service.

    Returns:
        CoachChatResponse containing the coach's message and any actions
    """
    ai_service = AIServiceFactory.create(model)
    return ai_service.generate(coach_prompt, chat_history, response_format, model)

