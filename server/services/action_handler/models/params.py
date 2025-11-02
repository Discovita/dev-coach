from pydantic import BaseModel, Field
from enums.coaching_phase import CoachingPhase
from enums.identity_category import IdentityCategory
from enums.get_to_know_you_questions import GetToKnowYouQuestions
from enums.identity_state import IdentityState


# NOTE: Cannot use the following pydantic model features on structured outputs from Open AI: Dict, Optional, Field(None)


class BaseParamsModel(BaseModel):
    """
    Base model for all action parameter models with shared configuration.

    All action parameter models extend this base class to inherit consistent
    validation behavior. The Config class sets `extra = "forbid"`, which means
    any fields not explicitly defined in the model will raise a validation error.
    This prevents typos, enforces strict schema compliance, and helps catch
    errors early when working with LLM-generated structured outputs.
    """

    class Config:
        extra = "forbid"


class SelectIdentityFocusParams(BaseParamsModel):
    new_focus: IdentityCategory = Field(
        ..., description="The new identity category to focus on"
    )


class SetCurrentIdentityParams(BaseParamsModel):
    identity_id: str = Field(
        ...,
        description="ID of the identity to set as the current identity being refined",
    )


class CreateIdentityParams(BaseParamsModel):
    name: str = Field(
        ..., description="A concise label for the identity (e.g., 'Creative Visionary')"
    )
    note: str = Field(
        ..., description="Initial note about why this identity was created"
    )
    category: IdentityCategory = Field(
        ..., description="Category this identity belongs to"
    )


class CreateMultipleIdentitiesParams(BaseParamsModel):
    identities: list[CreateIdentityParams] = Field(
        ...,
        description="List of identities to create, each with name, note, and category",
    )


class UpdateIdentityNameParams(BaseParamsModel):
    id: str = Field(..., description="ID of identity to update")
    name: str = Field(..., description="New name for the identity")


class UpdateIAmParams(BaseParamsModel):
    id: str = Field(..., description="ID of identity to update")
    i_am_statement: str = Field(
        ..., description="An 'I am' statement with a brief description"
    )


class UpdateIdentityVisualizationParams(BaseParamsModel):
    id: str = Field(..., description="ID of identity to update")
    visualization: str = Field(
        ...,
        description="A vivid description for the Identity that will be used in the creation of the image for this Identity",
    )


class UpdateIdentityParams(BaseParamsModel):
    id: str = Field(..., description="ID of identity to update")
    name: str = Field(..., description="New name for the identity")
    i_am_statement: str = Field(
        ..., description="An 'I am' statement with a brief description"
    )
    visualization: str = Field(
        ..., description="(Added in the visualization stage) A vivid mental image"
    )
    state: IdentityState = Field(
        ...,
        description="Current state of the identity (proposed, accepted, refinement complete)",
    )
    notes: list[str] = Field(
        ...,
        description="List of notes about the identity. These will get added to the existing notes",
    )
    category: IdentityCategory = Field(
        ..., description="Category this identity belongs to"
    )


class AcceptIdentityParams(BaseParamsModel):
    id: str = Field(..., description="ID of identity to accept")


class AcceptIdentityRefinementParams(BaseParamsModel):
    id: str = Field(..., description="ID of identity to mark as refinement complete")


class AcceptIdentityCommitmentParams(BaseParamsModel):
    id: str = Field(..., description="ID of identity to mark as commitment complete")


class AcceptIAmParams(BaseParamsModel):
    id: str = Field(
        ..., description="ID of identity to mark as i_am_statement complete"
    )


class AcceptIdentityVisualizationParams(BaseParamsModel):
    id: str = Field(..., description="ID of identity to mark as visualization complete")


class TransitionPhaseParams(BaseParamsModel):
    to_phase: CoachingPhase = Field(..., description="State to transition to")


# TODO: remove this as UpdateIdentityParams covers this already.
class AddIdentityNoteParams(BaseParamsModel):
    id: str = Field(..., description="ID of identity to add a note to")
    note: str = Field(..., description="Note to add to the identity")


class SkipIdentityCategoryParams(BaseParamsModel):
    category: IdentityCategory = Field(
        ..., description="Category to skip in the identity brainstorming phase"
    )


class UnskipIdentityCategoryParams(BaseParamsModel):
    category: IdentityCategory = Field(
        ..., description="Category to unskip in the identity brainstorming phase"
    )


class UpdateWhoYouAreParams(BaseParamsModel):
    who_you_are: list[str] = Field(
        ...,
        description="List of 'who you are' identities provided by the user",
    )


class UpdateWhoYouWantToBeParams(BaseParamsModel):
    who_you_want_to_be: list[str] = Field(
        ...,
        description="List of 'who you want to be' identities provided by the user",
    )


class AddUserNoteParams(BaseParamsModel):
    notes: list[str] = Field(
        description="List of notes to add about the user. A separate UserNote will be created for each entry in the list"
    )


class UpdateUserNoteItem(BaseParamsModel):
    id: str = Field(..., description="UUID of the user note to update")
    note: str = Field(..., description="The new note text")


class UpdateUserNoteParams(BaseParamsModel):
    notes: list[UpdateUserNoteItem] = Field(
        ..., description="List of user notes to update, each with id and new note text."
    )


class DeleteUserNoteParams(BaseParamsModel):
    ids: list[str] = Field(..., description="List of user note IDs to delete.")


class UpdateAskedQuestionsParams(BaseParamsModel):
    asked_question: GetToKnowYouQuestions = Field(
        ...,
        description="A single question that has been asked during the Get To Know You phase",
    )


class ShowIntroductionCannedResponseComponentParams(BaseParamsModel):
    show_introduction_canned_response_component: bool = Field(
        ..., description="Whether to show the introduction canned response component"
    )


class ShowAcceptIAMComponentParams(BaseParamsModel):
    id: str = Field(
        ..., description="ID of identity for i_am_statement acceptance component"
    )
    i_am_statement: str = Field(
        ..., description="I Am statement to propose to the user for acceptance"
    )


class ShowCombineIdentitiesParams(BaseParamsModel):
    identity_id_a: str = Field(..., description="ID of the first identity to combine")
    identity_id_b: str = Field(..., description="ID of the second identity to combine")


class CombineIdentitiesParams(BaseParamsModel):
    identity_id_a: str = Field(..., description="ID of the first identity to combine")
    identity_id_b: str = Field(..., description="ID of the second identity to combine")


class PersistCombineIdentitiesParams(BaseParamsModel):
    identity_id_a: str = Field(..., description="ID of the first identity to combine")
    identity_id_b: str = Field(..., description="ID of the second identity to combine")
    coach_message_id: str = Field(
        ..., description="ID of the coach message to persist the component to"
    )
