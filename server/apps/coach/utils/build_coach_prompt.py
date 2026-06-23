"""
Utility to build the prompt that will be sent to the AI coach.

The prompt includes all the context the coach needs to generate an appropriate
response, including the user's current phase, identities, and conversation history.
"""

from typing import Any, Dict, Optional, Tuple, Union

from pydantic import BaseModel

from apps.coach_states.models import CoachState
from apps.users.models import User
from enums.ai import AIModel
from services.logger import configure_logging
from services.prompt_manager.manager import PromptManager

log = configure_logging(__name__, log_level="INFO")


def build_coach_prompt(
    user: User,
    model: AIModel,
    prompt_versions: Optional[Dict[str, int]] = None,
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
        prompt_versions: Optional map of coaching-phase value -> prompt version
            to pin for that phase. Defaults to the latest active prompt for
            every phase; only the phases present in the map are overridden, and
            an override is applied only while the user is actually in that phase
            (so a version pinned for testing one phase never leaks into the
            prompts used after the conversation transitions onward). Used by the
            eval harness to run before/after comparisons against a specific
            prompt version.

    Returns:
        Tuple of (prompt_text, response_format)
        - prompt_text: The full prompt to send to the AI
        - response_format: The format specification for the AI's response
    """
    log.debug(f"Building coach prompt for user {user.id} with model {model}")

    # Resolve the version override for the user's CURRENT phase only. This keeps
    # a pinned version scoped to the phase under test even though a single
    # conversation can transition across several phases.
    version_override = None
    if prompt_versions:
        current_phase = CoachState.objects.get(user=user).current_phase
        version_override = prompt_versions.get(current_phase)

    prompt_manager = PromptManager()
    coach_prompt, response_format = prompt_manager.create_chat_prompt(
        user=user, model=model, version_override=version_override
    )
    return coach_prompt, response_format
