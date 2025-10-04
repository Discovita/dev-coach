from pydantic import BaseModel, Field
from typing import List, Optional
from enums.coaching_phase import CoachingPhase
from enums.identity_category import IdentityCategory
from enums.get_to_know_you_questions import GetToKnowYouQuestions
from enums.identity_state import IdentityState


# NOTE: Cannot use the following pydantic model features on structured outputs from Open AI: Dict, Optional, Field(None)


class SelectIdentityFocusParams(BaseModel):
    new_focus: IdentityCategory = Field(
        ..., description="The new identity category to focus on"
    )

    class Config:
        extra = "forbid"


class SetCurrentIdentityParams(BaseModel):
    identity_id: str = Field(
        ..., description="ID of the identity to set as the current identity being refined"
    )

    class Config:
        extra = "forbid"


class CreateIdentityParams(BaseModel):
    name: str = Field(
        ..., description="A concise label for the identity (e.g., 'Creative Visionary')"
    )
    note: str = Field(
        ..., description="Initial note about why this identity was created"
    )
    category: IdentityCategory = Field(
        ..., description="Category this identity belongs to"
    )

    class Config:
        extra = "forbid"


class CreateMultipleIdentitiesParams(BaseModel):
    identities: list[CreateIdentityParams] = Field(
        ..., description="List of identities to create, each with name, note, and category"
    )

    class Config:
        extra = "forbid"


class UpdateIdentityNameParams(BaseModel):
    id: str = Field(..., description="ID of identity to update")
    name: str = Field(..., description="New name for the identity")

    class Config:
        extra = "forbid"


class UpdateIdentityAffirmationParams(BaseModel):
    id: str = Field(..., description="ID of identity to update")
    affirmation: str = Field(
        ..., description="An 'I am' statement with a brief description"
    )

    class Config:
        extra = "forbid"


class UpdateIdentityVisualizationParams(BaseModel):
    id: str = Field(..., description="ID of identity to update")
    visualization: str = Field(
        ..., description="A vivid description for the Identity that will be used in the creation of the image for this Identity"
    )

    class Config:
        extra = "forbid"


class UpdateIdentityParams(BaseModel):
    id: str = Field(..., description="ID of identity to update")
    name: str = Field(..., description="New name for the identity")
    affirmation: str = Field(
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

    class Config:
        extra = "forbid"


class AcceptIdentityParams(BaseModel):
    id: str = Field(..., description="ID of identity to accept")

    class Config:
        extra = "forbid"


class AcceptIdentityRefinementParams(BaseModel):
    id: str = Field(..., description="ID of identity to mark as refinement complete")

    class Config:
        extra = "forbid"


class AcceptIdentityAffirmationParams(BaseModel):
    id: str = Field(..., description="ID of identity to mark as affirmation complete")

    class Config:
        extra = "forbid"


class AcceptIdentityVisualizationParams(BaseModel):
    id: str = Field(..., description="ID of identity to mark as visualization complete")

    class Config:
        extra = "forbid"


class TransitionPhaseParams(BaseModel):
    to_phase: CoachingPhase = Field(..., description="State to transition to")

    class Config:
        extra = "forbid"


# TODO: remove this as UpdateIdentityParams covers this already.
class AddIdentityNoteParams(BaseModel):
    id: str = Field(..., description="ID of identity to add a note to")
    note: str = Field(..., description="Note to add to the identity")

    class Config:
        extra = "forbid"


class SkipIdentityCategoryParams(BaseModel):
    category: IdentityCategory = Field(
        ..., description="Category to skip in the identity brainstorming phase"
    )

    class Config:
        extra = "forbid"


class UnskipIdentityCategoryParams(BaseModel):
    category: IdentityCategory = Field(
        ..., description="Category to unskip in the identity brainstorming phase"
    )

    class Config:
        extra = "forbid"


class UpdateWhoYouAreParams(BaseModel):
    who_you_are: list[str] = Field(
        ...,
        description="List of 'who you are' identities provided by the user",
    )

    class Config:
        extra = "forbid"


class UpdateWhoYouWantToBeParams(BaseModel):
    who_you_want_to_be: list[str] = Field(
        ...,
        description="List of 'who you want to be' identities provided by the user",
    )

    class Config:
        extra = "forbid"


class AddUserNoteParams(BaseModel):
    notes: list[str] = Field(
        description="List of notes to add about the user. A separate UserNote will be created for each entry in the list"
    )

    class Config:
        extra = "forbid"


class UpdateUserNoteItem(BaseModel):
    id: str = Field(..., description="UUID of the user note to update")
    note: str = Field(..., description="The new note text")

    class Config:
        extra = "forbid"


class UpdateUserNoteParams(BaseModel):
    notes: list[UpdateUserNoteItem] = Field(
        ..., description="List of user notes to update, each with id and new note text."
    )

    class Config:
        extra = "forbid"


class DeleteUserNoteParams(BaseModel):
    ids: list[str] = Field(
        ..., description="List of user note IDs to delete."
    )

    class Config:
        extra = "forbid"


class UpdateAskedQuestionsParams(BaseModel):
    asked_questions: List[GetToKnowYouQuestions] = Field(
        ...,
        description="List of questions that have been asked during the Get To Know You phase",
    )

    class Config:
        extra = "forbid"


class ShowIntroductionCannedResponseComponentParams(BaseModel):
    show_introduction_canned_response_component: bool = Field(
        ..., description="Whether to show the introduction canned response component"
    )

    class Config:
        extra = "forbid"


class ShowAcceptIAMComponentParams(BaseModel):
    id: str = Field(..., description="ID of identity for affirmation acceptance component")
    affirmation: str = Field(
        ..., description="Affirmation to propose to the user for acceptance"
    )

    class Config:
        extra = "forbid"


class ShowWarmupTextComponentParams(BaseModel):
    enabled: bool = Field(
        ..., description="Whether to show the warmup text component"
    )

    class Config:
        extra = "forbid"


class ShowBrainstormingIdentitiesParams(BaseModel):
    enabled: bool = Field(
        ..., description="Whether to show the brainstorming identities component"
    )

    class Config:
        extra = "forbid"
