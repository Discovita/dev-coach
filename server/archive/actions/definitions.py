"""OpenAI function definitions for coach actions."""

from typing import List
from .service import ActionDefinitionService

_service = ActionDefinitionService()

def get_available_actions() -> List[dict]:
    """Get available actions as OpenAI function definitions."""
    return _service.get_openai_schema()
