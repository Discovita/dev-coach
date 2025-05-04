from pydantic import BaseModel, Field
from .params import (
    SelectIdentityFocusParams,
    CreateIdentityParams,
    UpdateIdentityParams,
    AcceptIdentityParams,
    AcceptIdentityRefinementParams,
    TransitionStateParams,
    AddIdentityNoteParams,
)


class SelectIdentityFocusAction(BaseModel):
    params: SelectIdentityFocusParams = Field(
        ..., description="Parameters for selecting an identity to focus on."
    )


class CreateIdentityAction(BaseModel):
    params: CreateIdentityParams = Field(
        ..., description="Parameters for creating a new identity."
    )


class UpdateIdentityAction(BaseModel):
    params: UpdateIdentityParams = Field(
        ..., description="Parameters for updating an identity."
    )


class AcceptIdentityAction(BaseModel):
    params: AcceptIdentityParams = Field(
        ..., description="Parameters for accepting an identity."
    )


class AcceptIdentityRefinementAction(BaseModel):
    params: AcceptIdentityRefinementParams = Field(
        ..., description="Parameters for marking an identity as refinement complete."
    )


class TransitionStateAction(BaseModel):
    params: TransitionStateParams = Field(
        ..., description="Parameters for transitioning state."
    )


class AddIdentityNoteAction(BaseModel):
    params: AddIdentityNoteParams = Field(
        ..., description="Parameters for adding a note to an identity."
    )
