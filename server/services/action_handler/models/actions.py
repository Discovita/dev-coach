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


# TODO: Consider using a base model for Action models
class SelectIdentityFocusAction(BaseModel):
    params: SelectIdentityFocusParams = Field(
        ..., description="Parameters for selecting an identity to focus on."
    )

    class Config:
        extra = "forbid"


class CreateIdentityAction(BaseModel):
    params: CreateIdentityParams = Field(
        ..., description="Parameters for creating a new identity."
    )

    class Config:
        extra = "forbid"


class UpdateIdentityAction(BaseModel):
    params: UpdateIdentityParams = Field(
        ..., description="Parameters for updating an identity."
    )

    class Config:
        extra = "forbid"


class AcceptIdentityAction(BaseModel):
    params: AcceptIdentityParams = Field(
        ..., description="Parameters for accepting an identity."
    )

    class Config:
        extra = "forbid"


class AcceptIdentityRefinementAction(BaseModel):
    params: AcceptIdentityRefinementParams = Field(
        ..., description="Parameters for marking an identity as refinement complete."
    )

    class Config:
        extra = "forbid"


class TransitionStateAction(BaseModel):
    params: TransitionStateParams = Field(
        ..., description="Parameters for transitioning state."
    )

    class Config:
        extra = "forbid"


class AddIdentityNoteAction(BaseModel):
    params: AddIdentityNoteParams = Field(
        ..., description="Parameters for adding a note to an identity."
    )

    class Config:
        extra = "forbid"
