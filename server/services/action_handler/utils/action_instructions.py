"""
Action instructions for prompt generation.

This module provides structured action instructions that can be included in prompts
for the Discovita coaching system. It guides AI models on the available actions they can take during generation.
"""

from typing import Dict, List

# Import the ActionType enum for all available coaching actions
from enums.action_type import ActionType

# Import the action models for each action type
from services.action_handler.models.actions import (
    SelectIdentityFocusAction,
    CreateIdentityAction,
    UpdateIdentityAction,
    AcceptIdentityAction,
    AcceptIdentityRefinementAction,
    TransitionPhaseAction,
    AddIdentityNoteAction,
    SkipIdentityCategoryAction,
    UnskipIdentityCategoryAction,
    UpdateWhoYouAreAction,
    UpdateWhoYouWantToBeAction,
    AddUserNoteAction,
)

# Map ActionType to their parameter models and descriptions for prompt generation
# Each entry should have a clear, concise description and the corresponding Pydantic model
ACTION_PARAMS = {
    ActionType.SELECT_IDENTITY_FOCUS: {
        "description": "Select an identity to focus on.",
        "model": SelectIdentityFocusAction,
    },
    ActionType.CREATE_IDENTITY: {
        "description": "Create a new identity for the user.",
        "model": CreateIdentityAction,
    },
    ActionType.UPDATE_IDENTITY: {
        "description": "Update the details of an existing identity.",
        "model": UpdateIdentityAction,
    },
    ActionType.ACCEPT_IDENTITY: {
        "description": "Accept an identity as valid or complete.",
        "model": AcceptIdentityAction,
    },
    ActionType.ACCEPT_IDENTITY_REFINEMENT: {
        "description": "Mark an identity as refinement complete.",
        "model": AcceptIdentityRefinementAction,
    },
    ActionType.TRANSITION_PHASE: {
        "description": "Transition the coaching state to a new state.",
        "model": TransitionPhaseAction,
    },
    ActionType.ADD_IDENTITY_NOTE: {
        "description": "Add a note to an identity.",
        "model": AddIdentityNoteAction,
    },
    ActionType.SKIP_IDENTITY_CATEGORY: {
        "description": "Add this identity category to the list of skipped categories.",
        "model": SkipIdentityCategoryAction,
    },
    ActionType.UNSKIP_IDENTITY_CATEGORY: {
        "description": "Remove this identity category from the list of skipped categories.",
        "model": UnskipIdentityCategoryAction,
    },
    ActionType.UPDATE_WHO_YOU_ARE: {
        "description": "Update the list of the user's current identities. You must pass the complete list of all identities that will go in the final list, not just the ones that have changed.",
        "model": UpdateWhoYouAreAction,
    },
    ActionType.UPDATE_WHO_YOU_WANT_TO_BE: {
        "description": "Update the list of the user's aspirational identities. You must pass the complete list of all identities that will go in the final list, not just the ones that have changed.",
        "model": UpdateWhoYouWantToBeAction,
    },
    ActionType.ADD_USER_NOTE: {
        "description": "Add a new note about the user. Use this to store important facts or context about the user that should be remembered for the long term.",
        "model": AddUserNoteAction,
    },
}

# Generate instruction text for each action type
# This dictionary will map ActionType to a markdown-formatted instruction string
ACTION_INSTRUCTIONS: Dict[ActionType, str] = {}

for action_type, params_info in ACTION_PARAMS.items():
    description = params_info.get("description", "")
    params_model = params_info.get("model")

    # Generate the JSON schema for the action's parameters using Pydantic
    schema = params_model.model_json_schema()

    # Format the complete instruction for this action type
    ACTION_INSTRUCTIONS[action_type] = (
        f"""**{action_type.value}**: {description}\n```json\n{schema}\n```"""
    )


# TODO: The current implementation has the prompt spelling out what the "action guidelines" are. Maybe we can proceduralize this and hard code them and add them here based on what the actions are.
def get_action_instructions(action_types: List[ActionType]) -> str:
    """
    Generate action instructions for the specified action types.
    Args:
        action_types (List[ActionType]): The list of action types to include in the instructions.
    Returns:
        str: Markdown-formatted instructions for the allowed actions, including JSON schemas.
    """
    if not action_types:
        return ""

    # Filter to include only the requested actions
    filtered_instructions = [
        ACTION_INSTRUCTIONS[action_type]
        for action_type in action_types
        if action_type in ACTION_INSTRUCTIONS
    ]

    if not filtered_instructions:
        return ""

    # Format the instructions with a header and footer
    header = "# Available Actions\nYou can perform the following actions:\n"
    action_content = "\n".join(filtered_instructions)
    footer = "\n> For each action, the params field must match the schema shown in the example, including all nested objects."

    return f"{header}{action_content}{footer}"
