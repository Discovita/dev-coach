from pydantic import BaseModel, Field
from enums.identity_category import IdentityCategory
from enums.coaching_phase import CoachingPhase
from enums.identity_state import IdentityState


# NOTE: Cannot use the following pydantic model features on structured outputs from Open AI: Dict, Optional, Field(None)


class SelectIdentityFocusParams(BaseModel):
    new_focus: IdentityCategory = Field(
        ..., description="The new identity category to focus on"
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
    note: str

    class Config:
        extra = "forbid"
