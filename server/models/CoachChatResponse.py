from pydantic import BaseModel, Field
from typing import List, Optional
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
)
# NOTE: The AddUserNoteAction is deliberately skipped here because that action is used by the Sentinel


class CoachChatResponse(BaseModel):
    """
    Response model for a coach step.
    Each field is an optional action, named after the action, and typed to the corresponding action model.
    The 'message' field is always required and contains the coach's response message.
    """

    message: str = Field(..., description="Coach's response message")

    select_identity_focus: Optional[SelectIdentityFocusAction] = Field(
        default=None, description="Perform the select_identity_focus action."
    )
    create_identity: Optional[CreateIdentityAction] = Field(
        default=None, description="Perform the create_identity action."
    )
    update_identity: Optional[UpdateIdentityAction] = Field(
        default=None, description="Perform the update_identity action."
    )
    accept_identity: Optional[AcceptIdentityAction] = Field(
        default=None, description="Perform the accept_identity action."
    )
    accept_identity_refinement: Optional[AcceptIdentityRefinementAction] = Field(
        default=None, description="Perform the accept_identity_refinement action."
    )
    transition_phase: Optional[TransitionPhaseAction] = Field(
        default=None, description="Perform the transition_phase action."
    )
    add_identity_note: Optional[AddIdentityNoteAction] = Field(
        default=None, description="Perform the add_identity_note action."
    )
    skip_identity_category: Optional[SkipIdentityCategoryAction] = Field(
        default=None, description="Perform the skip_identity_category action."
    )
    unskip_identity_category: Optional[UnskipIdentityCategoryAction] = Field(
        default=None, description="Perform the unskip_identity_category action."
    )
    update_who_you_are: Optional[UpdateWhoYouAreAction] = Field(
        default=None, description="Perform the update_who_you_are action."
    )
    update_who_you_want_to_be: Optional[UpdateWhoYouWantToBeAction] = Field(
        default=None, description="Perform the update_who_you_want_to_be action."
    )
