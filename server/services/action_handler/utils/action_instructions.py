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
    SetCurrentIdentityAction,
    CreateIdentityAction,
    CreateMultipleIdentitiesAction,
    UpdateIdentityNameAction,
    UpdateIdentityAffirmationAction,
    UpdateIdentityVisualizationAction,
    UpdateIdentityAction,
    AcceptIdentityAction,
    AcceptIdentityRefinementAction,
    AcceptIdentityAffirmationAction,
    AcceptIdentityVisualizationAction,
    TransitionPhaseAction,
    AddIdentityNoteAction,
    SkipIdentityCategoryAction,
    UnskipIdentityCategoryAction,
    UpdateWhoYouAreAction,
    UpdateWhoYouWantToBeAction,
    AddUserNoteAction,
    UpdateUserNoteAction,
    DeleteUserNoteAction,
    UpdateAskedQuestionsAction,
    ShowIntroductionCannedResponseComponentAction,
    ShowAcceptIAMComponentAction,
    ShowWarmupTextComponentAction,
)

# Map ActionType to their parameter models and descriptions for prompt generation
# Each entry should have a clear, concise description and the corresponding Pydantic model
ACTION_PARAMS = {
    ActionType.SELECT_IDENTITY_FOCUS: {
        "description": "Select the appropriate Identity Category to focus on.",
        "model": SelectIdentityFocusAction,
    },
    ActionType.SET_CURRENT_IDENTITY: {
        "description": "Set the current Identity to focus on for targeted changes",
        "model": SetCurrentIdentityAction,
    },
    ActionType.CREATE_IDENTITY: {
        "description": "Creates a new Identity for the user. DO NOT create duplicate Identities. Ask yourself - Has the user expressed consent to create this Identity? If the answer is no, don't create a new one. DO NOT preemptively create Identities for the user.",
        "model": CreateIdentityAction,
    },
    ActionType.CREATE_MULTIPLE_IDENTITIES: {
        "description": "Creates multiple new Identities for the user at once. Use this when the user has provided multiple identity concepts that should all be created together. DO NOT create duplicate Identities. Ask yourself - Has the user expressed consent to create these Identities? If the answer is no, don't create them. DO NOT preemptively create Identities for the user.",
        "model": CreateMultipleIdentitiesAction,
    },
    ActionType.UPDATE_IDENTITY_NAME: {
        "description": "Update the name of an existing Identity.",
        "model": UpdateIdentityNameAction,
    },
    ActionType.UPDATE_IDENTITY_AFFIRMATION: {
        "description": "Update the affirmation of an existing Identity.",
        "model": UpdateIdentityAffirmationAction,
    },
    ActionType.UPDATE_IDENTITY_VISUALIZATION: {
        "description": "Update the visualization of an existing Identity.",
        "model": UpdateIdentityVisualizationAction,
    },
    ActionType.UPDATE_IDENTITY: {
        "description": "Update the details of an existing Identity. ",
        "model": UpdateIdentityAction,
    },
    ActionType.ACCEPT_IDENTITY: {
        "description": "Mark an Identity as accepted.",
        "model": AcceptIdentityAction,
    },
    ActionType.ACCEPT_IDENTITY_REFINEMENT: {
        "description": "Mark an Identity as refinement_complete.",
        "model": AcceptIdentityRefinementAction,
    },
    ActionType.ACCEPT_IDENTITY_AFFIRMATION: {
        "description": "Mark an Identity as affirmation_complete.",
        "model": AcceptIdentityAffirmationAction,
    },
    ActionType.ACCEPT_IDENTITY_VISUALIZATION: {
        "description": "Mark an Identity as visualization_complete.",
        "model": AcceptIdentityVisualizationAction,
    },
    ActionType.TRANSITION_PHASE: {
        "description": "Move to the next Coaching Phase.",
        "model": TransitionPhaseAction,
    },
    ActionType.ADD_IDENTITY_NOTE: {
        "description": "Add a note to an Identity.",
        "model": AddIdentityNoteAction,
    },
    ActionType.SKIP_IDENTITY_CATEGORY: {
        "description": "Add this Identity category to the list of skipped categories.",
        "model": SkipIdentityCategoryAction,
    },
    ActionType.UNSKIP_IDENTITY_CATEGORY: {
        "description": "Remove this Identity category from the list of skipped categories.",
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
    ActionType.UPDATE_USER_NOTE: {
        "description": "Update one or more user notes by ID. Each object must have an id and the new note text.",
        "model": UpdateUserNoteAction,
    },
    ActionType.DELETE_USER_NOTE: {
        "description": "Delete one or more user notes by ID. Each ID must correspond to a user note.",
        "model": DeleteUserNoteAction,
    },
    ActionType.UPDATE_ASKED_QUESTIONS: {
        "description": "Update the list of questions that have been asked during the Get To Know You phase. You must pass the complete list of all questions that have been asked, not just the ones that have changed.",
        "model": UpdateAskedQuestionsAction,
    },
    ActionType.SHOW_INTRODUCTION_CANNED_RESPONSE_COMPONENT: {
        "description": "Show an introduction canned response component to the user with pre-written response buttons for convenience during the introduction phase. Use this when asking the user any questions. The way this gets used is when you ask the user a question, set this to true and the component will be shown to the user allowing them to answer more easily.",
        "model": ShowIntroductionCannedResponseComponentAction,
    },
    ActionType.SHOW_ACCEPT_I_AM_COMPONENT: {
        "description": "Show an 'Accept I Am' component asking the user to accept the proposed affirmation or keep working on it. Pass the identity id and the proposed affirmation.",
        "model": ShowAcceptIAMComponentAction,
    },
    ActionType.SHOW_WARMUP_TEXT_COMPONENT: {
        "description": "Show a warmup text block (markdown) before/after the coach message. Use for adding the users who_you_are and who_you_want_to_be information to the coach message.",
        "model": ShowWarmupTextComponentAction,
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
