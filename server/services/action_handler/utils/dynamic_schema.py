from typing import Optional, Dict, Type, List
from pydantic import Field, create_model, BaseModel
from enums.action_type import ActionType
from services.action_handler.models.actions import *

from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")

ACTION_TYPE_TO_MODEL: Dict[ActionType, Type[BaseModel]] = {
    ActionType.SELECT_IDENTITY_FOCUS: SelectIdentityFocusAction,
    ActionType.SET_CURRENT_IDENTITY: SetCurrentIdentityAction,
    ActionType.CREATE_IDENTITY: CreateIdentityAction,
    ActionType.CREATE_MULTIPLE_IDENTITIES: CreateMultipleIdentitiesAction,
    ActionType.UPDATE_IDENTITY_NAME: UpdateIdentityNameAction,
    ActionType.UPDATE_I_AM_STATEMENT: UpdateIAmAction,
    ActionType.UPDATE_IDENTITY_VISUALIZATION: UpdateIdentityVisualizationAction,
    ActionType.UPDATE_IDENTITY: UpdateIdentityAction,
    ActionType.ACCEPT_IDENTITY: AcceptIdentityAction,
    ActionType.ACCEPT_IDENTITY_REFINEMENT: AcceptIdentityRefinementAction,
    ActionType.ACCEPT_IDENTITY_COMMITMENT: AcceptIdentityCommitmentAction,
    ActionType.ACCEPT_I_AM_STATEMENT: AcceptIAmAction,
    ActionType.ACCEPT_IDENTITY_VISUALIZATION: AcceptIdentityVisualizationAction,
    ActionType.ARCHIVE_IDENTITY: ArchiveIdentityAction,
    ActionType.NEST_IDENTITY: NestIdentityAction,
    ActionType.TRANSITION_PHASE: TransitionPhaseAction,
    ActionType.ADD_IDENTITY_NOTE: AddIdentityNoteAction,
    ActionType.SKIP_IDENTITY_CATEGORY: SkipIdentityCategoryAction,
    ActionType.UNSKIP_IDENTITY_CATEGORY: UnskipIdentityCategoryAction,
    ActionType.UPDATE_WHO_YOU_ARE: UpdateWhoYouAreAction,
    ActionType.UPDATE_WHO_YOU_WANT_TO_BE: UpdateWhoYouWantToBeAction,
    ActionType.ADD_USER_NOTE: AddUserNoteAction,
    ActionType.UPDATE_USER_NOTE: UpdateUserNoteAction,
    ActionType.DELETE_USER_NOTE: DeleteUserNoteAction,
    ActionType.UPDATE_ASKED_QUESTIONS: UpdateAskedQuestionsAction,
    ActionType.SHOW_INTRODUCTION_CANNED_RESPONSE_COMPONENT: ShowIntroductionCannedResponseComponentAction,
    ActionType.SHOW_ACCEPT_I_AM_COMPONENT: ShowAcceptIAMComponentAction,
    ActionType.SHOW_COMBINE_IDENTITIES: ShowCombineIdentitiesAction,
    ActionType.COMBINE_IDENTITIES: CombineIdentitiesAction,
    ActionType.PERSIST_COMBINE_IDENTITIES: PersistCombineIdentitiesAction,
}


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
