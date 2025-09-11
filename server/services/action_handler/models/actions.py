from pydantic import BaseModel, Field
from .params import (
    SelectIdentityFocusParams,
    SetCurrentIdentityParams,
    CreateIdentityParams,
    UpdateIdentityNameParams,
    UpdateIdentityAffirmationParams,
    UpdateIdentityVisualizationParams,
    UpdateIdentityParams,
    AcceptIdentityParams,
    AcceptIdentityRefinementParams,
    AcceptIdentityAffirmationParams,
    AcceptIdentityVisualizationParams,
    TransitionPhaseParams,
    AddIdentityNoteParams,
    SkipIdentityCategoryParams,
    UpdateWhoYouAreParams,
    UpdateWhoYouWantToBeParams,
    UnskipIdentityCategoryParams,
    AddUserNoteParams,
    UpdateUserNoteParams,
    DeleteUserNoteParams,
    UpdateAskedQuestionsParams,
    ShowIntroductionCannedResponseComponentParams,
)


# TODO: Consider using a base model for Action models
class SelectIdentityFocusAction(BaseModel):
    params: SelectIdentityFocusParams = Field(
        ..., description="Parameters for selecting an identity to focus on."
    )

    class Config:
        extra = "forbid"


class SetCurrentIdentityAction(BaseModel):
    params: SetCurrentIdentityParams = Field(
        ..., description="Parameters for setting the current identity being refined."
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


class UpdateIdentityNameAction(BaseModel):
    params: UpdateIdentityNameParams = Field(
        ..., description="Parameters for updating an identity's name."
    )

    class Config:
        extra = "forbid"


class UpdateIdentityAffirmationAction(BaseModel):
    params: UpdateIdentityAffirmationParams = Field(
        ..., description="Parameters for updating an identity's affirmation."
    )

    class Config:
        extra = "forbid"


class UpdateIdentityVisualizationAction(BaseModel):
    params: UpdateIdentityVisualizationParams = Field(
        ..., description="Parameters for updating an identity's visualization."
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


class AcceptIdentityAffirmationAction(BaseModel):
    params: AcceptIdentityAffirmationParams = Field(
        ..., description="Parameters for marking an identity as affirmation complete."
    )

    class Config:
        extra = "forbid"


class AcceptIdentityVisualizationAction(BaseModel):
    params: AcceptIdentityVisualizationParams = Field(
        ..., description="Parameters for marking an identity as visualization complete."
    )

    class Config:
        extra = "forbid"


class TransitionPhaseAction(BaseModel):
    params: TransitionPhaseParams = Field(
        ..., description="Parameters for transitioning the coaching phase."
    )

    class Config:
        extra = "forbid"


class AddIdentityNoteAction(BaseModel):
    params: AddIdentityNoteParams = Field(
        ..., description="Parameters for adding a note to an identity."
    )

    class Config:
        extra = "forbid"


class SkipIdentityCategoryAction(BaseModel):
    params: SkipIdentityCategoryParams = Field(
        ..., description="Parameters for skipping an identity category."
    )

    class Config:
        extra = "forbid"


class UpdateWhoYouAreAction(BaseModel):
    params: UpdateWhoYouAreParams = Field(
        ..., description="Parameters for updating 'who you are' identities."
    )

    class Config:
        extra = "forbid"


class UpdateWhoYouWantToBeAction(BaseModel):
    params: UpdateWhoYouWantToBeParams = Field(
        ..., description="Parameters for updating 'who you want to be' identities."
    )

    class Config:
        extra = "forbid"


class UnskipIdentityCategoryAction(BaseModel):
    params: UnskipIdentityCategoryParams = Field(
        ..., description="Parameters for unskipping an identity category."
    )

    class Config:
        extra = "forbid"


class AddUserNoteAction(BaseModel):
    params: AddUserNoteParams = Field(
        description="Parameters for adding a note (or notes) to the users notes."
    )

    class Config:
        extra = "forbid"


class UpdateUserNoteAction(BaseModel):
    params: UpdateUserNoteParams = Field(
        ..., description="Parameters for updating user notes by id."
    )

    class Config:
        extra = "forbid"


class DeleteUserNoteAction(BaseModel):
    params: DeleteUserNoteParams = Field(
        ..., description="Parameters for deleting user notes by id."
    )

    class Config:
        extra = "forbid"


class UpdateAskedQuestionsAction(BaseModel):
    params: UpdateAskedQuestionsParams = Field(
        ..., description="Parameters for updating asked questions list."
    )

    class Config:
        extra = "forbid"


class ShowIntroductionCannedResponseComponentAction(BaseModel):
    params: ShowIntroductionCannedResponseComponentParams = Field(
        ..., description="Parameters for showing the canned response component."
    )

    class Config:
        extra = "forbid"