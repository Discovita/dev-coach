from typing import Optional, Dict, Type, List
from pydantic import Field, create_model, BaseModel
from enums.action_type import ActionType
from services.action_handler.models.actions import (
    SelectIdentityFocusAction,
    CreateIdentityAction,
    UpdateIdentityAction,
    AcceptIdentityAction,
    AcceptIdentityRefinementAction,
    TransitionStateAction,
    AddIdentityNoteAction,
)

ACTION_TYPE_TO_MODEL: Dict[ActionType, Type[BaseModel]] = {
    ActionType.SELECT_IDENTITY_FOCUS: SelectIdentityFocusAction,
    ActionType.CREATE_IDENTITY: CreateIdentityAction,
    ActionType.UPDATE_IDENTITY: UpdateIdentityAction,
    ActionType.ACCEPT_IDENTITY: AcceptIdentityAction,
    ActionType.ACCEPT_IDENTITY_REFINEMENT: AcceptIdentityRefinementAction,
    ActionType.TRANSITION_STATE: TransitionStateAction,
    ActionType.ADD_IDENTITY_NOTE: AddIdentityNoteAction,
}

from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


def build_dynamic_response_format(
    allowed_actions: List[str],
) -> Type[BaseModel]:
    """
    Dynamically build a Pydantic model for the response, where each allowed action is an
    optional field named after the action (ActionType.value), and typed to the action model.
    Always includes a required 'message' field for the coach's response message.
    The action types are stored as strings in the database, so we need to convert them to ActionType enum values.
    """
    fields = {
        # Always include the message field
        "message": (str, Field(..., description="Coach's response message")),
    }
    for action_type in allowed_actions:
        if isinstance(action_type, str):
            action_type = ActionType(action_type)
        action_model = ACTION_TYPE_TO_MODEL[action_type]
        fields[action_type.value] = (
            Optional[action_model],
            Field(description=f"Perform the {action_type.value} action."),
        )
    config = {"extra": "forbid"}

    dynamic_model = create_model("DynamicResponse", **fields, __config__=config)
    log.debug(f"Dynamic response model created with fields: {fields.keys()}")
    log.debug(f"Dynamic response model : {dynamic_model.schema_json(indent=2)}")
    return dynamic_model
