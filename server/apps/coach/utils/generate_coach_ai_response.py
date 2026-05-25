"""
Utility to generate the coach's response using AI.

This takes the prompt and conversation history and sends it to the AI service
to generate a personalized response from the coach.

Note on `chat_history`: in the current OpenAI service implementation the
history is omitted at the API boundary because the PromptManager has already
embedded it into `coach_prompt` via `append_recent_messages`. It is still
threaded through for future-provider compatibility and easier mocking.
PR 11 changed the contract from `list[ChatMessage]` to `list[str]` so that
component-bearing rows can carry their bracketed narration.
"""

from pydantic import BaseModel

from enums.ai import AIModel
from models.CoachChatResponse import CoachChatResponse
from services.ai import AIServiceFactory


def generate_coach_ai_response(
    coach_prompt: str,
    chat_history: list[str],
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
