"""Models for OpenAI function definitions."""

from typing import List, Optional
from pydantic import BaseModel, Field
from ..models.action import ActionType
from ..models.state import CoachingState
from ..models.identity import IdentityCategory

class SelectIdentityFocusParams(BaseModel):
    """Parameters for selecting an identity to focus on during refinement."""
    id: str = Field(..., description="ID of identity to focus on")

class CreateIdentityParams(BaseModel):
    """Parameters for creating a new identity."""
    description: str = Field(..., description="Description of the identity")
    note: str = Field(..., description="Initial note about why this identity was created")
    category: IdentityCategory = Field(..., description="Category this identity belongs to")

class UpdateIdentityParams(BaseModel):
    """Parameters for updating an identity."""
    id: str = Field(..., description="ID of identity to update")
    description: str = Field(..., description="Updated description")

class AcceptIdentityParams(BaseModel):
    """Parameters for accepting an identity (changing state from PROPOSED to ACCEPTED)."""
    id: str = Field(..., description="ID of identity to accept")

class AcceptIdentityRefinementParams(BaseModel):
    """Parameters for marking an identity as refinement complete (changing state from ACCEPTED to REFINEMENT_COMPLETE)."""
    id: str = Field(..., description="ID of identity to mark as refinement complete")

class TransitionStateParams(BaseModel):
    """Parameters for transitioning state."""
    to_state: CoachingState = Field(..., description="State to transition to")

class AddIdentityNoteParams(BaseModel):
    """Parameters for adding a note to an identity."""
    id: str = Field(..., description="ID of identity to add a note to")
    note: str = Field(..., description="Note to add to the identity")

class FunctionDefinition(BaseModel):
    """OpenAI function definition."""
    type: str = Field(default="function", description="Type of the function")
    name: str = Field(..., description="Name of the function")
    description: str = Field(..., description="Description of the function")
    parameters: dict = Field(..., description="Parameters schema")
