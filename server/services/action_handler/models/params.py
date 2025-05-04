from pydantic import BaseModel, Field
from enums.identity_category import IdentityCategory
from enums.coaching_state import CoachingState


class SelectIdentityFocusParams(BaseModel):
    id: str = Field(..., description="ID of identity to focus on")


class CreateIdentityParams(BaseModel):
    description: str = Field(..., description="Description of the identity")
    note: str = Field(
        ..., description="Initial note about why this identity was created"
    )
    category: IdentityCategory = Field(
        ..., description="Category this identity belongs to"
    )


class UpdateIdentityParams(BaseModel):
    id: str = Field(..., description="ID of identity to update")
    description: str = Field(..., description="Updated description")


class AcceptIdentityParams(BaseModel):
    id: str = Field(..., description="ID of identity to accept")


class AcceptIdentityRefinementParams(BaseModel):
    id: str = Field(..., description="ID of identity to mark as refinement complete")


class TransitionStateParams(BaseModel):
    to_state: CoachingState = Field(..., description="State to transition to")


class AddIdentityNoteParams(BaseModel):
    id: str = Field(..., description="ID of identity to add a note to")
    note: str = Field(..., description="Note to add to the identity")
