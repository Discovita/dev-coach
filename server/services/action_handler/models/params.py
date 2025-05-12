from typing import Optional
from pydantic import BaseModel, Field
from enums.identity_category import IdentityCategory
from enums.coaching_state import CoachingState
from enums.identity_state import IdentityState


class SelectIdentityFocusParams(BaseModel):
    new_focus: IdentityCategory = Field(
        ..., description="The new identity category to focus on"
    )

    class Config:
        extra = "forbid"


class CreateIdentityParams(BaseModel):
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
    name: Optional[str] = Field(None, description="New name for the identity")
    affirmation: Optional[str] = Field(
        None, description="An 'I am' statement with a brief description"
    )
    visualization: Optional[str] = Field(
        None, description="(Added in the visualization stage) A vivid mental image"
    )
    state: Optional[IdentityState] = Field(
        None,
        description="Current state of the identity (proposed, accepted, refinement complete)",
    )
    notes: Optional[list[str]] = Field(
        None,
        description="List of notes about the identity. These will get added to the existing notes",
    )
    category: Optional[IdentityCategory] = Field(
        None, description="Category this identity belongs to"
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


class TransitionStateParams(BaseModel):
    to_state: CoachingState = Field(..., description="State to transition to")

    class Config:
        extra = "forbid"

# TODO: remove this as UpdateIdentityParams covers this already. 
class AddIdentityNoteParams(BaseModel):
    id: str = Field(..., description="ID of identity to add a note to")
    note: str = Field(..., description="Note to add to the identity")

    class Config:
        extra = "forbid"
