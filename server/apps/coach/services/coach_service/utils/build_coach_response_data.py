"""
Utility to build the response data structure returned to the client.

This packages up the coach's message, the prompt that was used, and any
component configuration into the format expected by the frontend.
"""
from typing import Dict, Any
from models.components.ComponentConfig import ComponentConfig


def build_coach_response_data(
    coach_message: str,
    final_prompt: str,
    component_config: ComponentConfig | None = None,
) -> Dict[str, Any]:
    """
    Build the response data structure for the client.

    This creates a dictionary containing:
    - The coach's response message
    - The prompt that was used to generate it
    - Any component configuration for UI interactions (optional)

    Args:
        coach_message: The message text from the coach
        final_prompt: The full prompt that was sent to the AI
        component_config: Optional component configuration for UI interactions

    Returns:
        Dictionary containing the response data for the client
    """
    response_data = {
        "message": coach_message,
        "final_prompt": final_prompt,
    }

    if component_config:
        response_data["component"] = component_config.model_dump()

    return response_data

