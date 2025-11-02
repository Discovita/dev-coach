from pydantic import BaseModel, Field
from typing import List, Optional
from services.action_handler.models.actions import (
    SelectIdentityFocusAction,
    SetCurrentIdentityAction,
    CreateIdentityAction,
    CreateMultipleIdentitiesAction,
    UpdateIdentityAction,
    UpdateIdentityNameAction,
    UpdateIAmAction,
    UpdateIdentityVisualizationAction,
    AcceptIdentityAction,
    AcceptIdentityRefinementAction,
    AcceptIdentityCommitmentAction,
    AcceptIAmAction,
    AcceptIdentityVisualizationAction,
    TransitionPhaseAction,
    AddIdentityNoteAction,
    SkipIdentityCategoryAction,
    UnskipIdentityCategoryAction,
    UpdateWhoYouAreAction,
    UpdateWhoYouWantToBeAction,
    UpdateAskedQuestionsAction,
    ShowIntroductionCannedResponseComponentAction,
    ShowAcceptIAMComponentAction,
    ShowCombineIdentitiesAction,
    PersistCombineIdentitiesAction,
)

# NOTE: The AddUserNoteAction and UpdateUserNoteAction are deliberately skipped here because these actions are used by the Sentinel


class CoachChatResponse(BaseModel):
    """
    Response model for a coach step.
    Each field is an optional action, named after the action, and typed to the corresponding action model.
    The 'message' field is always required and contains the coach's response message.
    """

    message: str = Field(..., description="Coach's response message")

    create_identity: Optional[CreateIdentityAction] = Field(
        default=None, description="Perform the create_identity action."
    )
    create_multiple_identities: Optional[CreateMultipleIdentitiesAction] = Field(
        default=None, description="Perform the create_multiple_identities action."
    )
    update_identity: Optional[UpdateIdentityAction] = Field(
        default=None, description="Perform the update_identity action."
    )
    update_identity_name: Optional[UpdateIdentityNameAction] = Field(
        default=None, description="Perform the update_identity_name action."
    )
    update_i_am_statement: Optional[UpdateIAmAction] = Field(
        default=None, description="Perform the update_i_am_statement action."
    )
    update_identity_visualization: Optional[UpdateIdentityVisualizationAction] = Field(
        default=None, description="Perform the update_identity_visualization action."
    )
    accept_identity: Optional[AcceptIdentityAction] = Field(
        default=None, description="Perform the accept_identity action."
    )
    accept_identity_refinement: Optional[AcceptIdentityRefinementAction] = Field(
        default=None, description="Perform the accept_identity_refinement action."
    )
    accept_identity_commitment: Optional[AcceptIdentityCommitmentAction] = Field(
        default=None, description="Perform the accept_identity_commitment action."
    )
    accept_i_am_statement: Optional[AcceptIAmAction] = Field(
        default=None, description="Perform the accept_i_am_statement action."
    )
    accept_identity_visualization: Optional[AcceptIdentityVisualizationAction] = Field(
        default=None, description="Perform the accept_identity_visualization action."
    )
    add_identity_note: Optional[AddIdentityNoteAction] = Field(
        default=None, description="Perform the add_identity_note action."
    )
    transition_phase: Optional[TransitionPhaseAction] = Field(
        default=None, description="Perform the transition_phase action."
    )
    select_identity_focus: Optional[SelectIdentityFocusAction] = Field(
        default=None, description="Perform the select_identity_focus action."
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
    update_asked_questions: Optional[UpdateAskedQuestionsAction] = Field(
        default=None, description="Perform the update_asked_questions action."
    )
    set_current_identity: Optional[SetCurrentIdentityAction] = Field(
        default=None, description="Perform the set_current_identity action."
    )
    # Components
    show_introduction_canned_response_component: Optional[ShowIntroductionCannedResponseComponentAction] = Field(
        default=None, description="Show the introduction canned response component."
    )
    show_accept_i_am_component: Optional[ShowAcceptIAMComponentAction] = Field(
        default=None, description="Show the Accept I Am component."
    )
    show_combine_identities: Optional[ShowCombineIdentitiesAction] = Field(
        default=None, description="Show the combine identities component."
    )
    persist_combine_identities: Optional[PersistCombineIdentitiesAction] = Field(
        default=None, description="Persist the combine identities component for historical display."
    )
