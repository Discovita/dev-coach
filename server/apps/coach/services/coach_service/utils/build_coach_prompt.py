"""
Utility to build the prompt that will be sent to the AI coach.

The prompt includes all the context the coach needs to generate an appropriate
response, including the user's current phase, identities, and conversation history.
"""

from typing import Tuple, Union, Dict, Any
from apps.users.models import User
from enums.ai import AIModel
from pydantic import BaseModel
from services.prompt_manager.manager import PromptManager
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


def build_coach_prompt(
    user: User, model: AIModel
) -> Tuple[str, Union[BaseModel, Dict[str, Any]]]:
    """
    Build the prompt that will be sent to the AI coach.

    The prompt includes information about:
    - The user's current coaching phase
    - Their identities and progress
    - Instructions for how the coach should respond

    Args:
        user: The user to build the prompt for
        model: The AI model that will generate the response

    Returns:
        Tuple of (prompt_text, response_format)
        - prompt_text: The full prompt to send to the AI
        - response_format: The format specification for the AI's response
    """
    log.debug(f"Building coach prompt for user {user.id} with model {model}")
    prompt_manager = PromptManager()
    coach_prompt, response_format = prompt_manager.create_chat_prompt(
        user=user, model=model
    )
    return coach_prompt, response_format
