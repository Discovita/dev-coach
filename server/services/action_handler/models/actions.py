from pydantic import BaseModel, Field
from .params import *


class BaseActionModel(BaseModel):
    """
    Base model for all action models with shared configuration.

    All action models extend this base class to inherit consistent
    validation behavior. The Config class sets `extra = "forbid"`, which means
    any fields not explicitly defined in the model will raise a validation error.
    This prevents typos, enforces strict schema compliance, and helps catch
    errors early when working with LLM-generated structured outputs.
    """

    class Config:
        extra = "forbid"


class SelectIdentityFocusAction(BaseActionModel):
    params: SelectIdentityFocusParams = Field(
        ..., description="Parameters for selecting an identity to focus on."
    )


class SetCurrentIdentityAction(BaseActionModel):
    params: SetCurrentIdentityParams = Field(
        ..., description="Parameters for setting the current identity being refined."
    )


class CreateIdentityAction(BaseActionModel):
    params: CreateIdentityParams = Field(
        ..., description="Parameters for creating a new identity."
    )


class CreateMultipleIdentitiesAction(BaseActionModel):
    params: CreateMultipleIdentitiesParams = Field(
        ..., description="Parameters for creating multiple identities."
    )


class UpdateIdentityAction(BaseActionModel):
    params: UpdateIdentityParams = Field(
        ..., description="Parameters for updating an identity."
    )


class UpdateIdentityNameAction(BaseActionModel):
    params: UpdateIdentityNameParams = Field(
        ..., description="Parameters for updating an identity's name."
    )


class UpdateIAmAction(BaseActionModel):
    params: UpdateIAmParams = Field(
        ..., description="Parameters for updating an identity's i_am_statement."
    )


class UpdateIdentityVisualizationAction(BaseActionModel):
    params: UpdateIdentityVisualizationParams = Field(
        ..., description="Parameters for updating an identity's visualization."
    )


class AcceptIdentityAction(BaseActionModel):
    params: AcceptIdentityParams = Field(
        ..., description="Parameters for accepting an identity."
    )


class AcceptIdentityRefinementAction(BaseActionModel):
    params: AcceptIdentityRefinementParams = Field(
        ..., description="Parameters for marking an identity as refinement complete."
    )


class AcceptIdentityCommitmentAction(BaseActionModel):
    params: AcceptIdentityCommitmentParams = Field(
        ..., description="Parameters for marking an identity as commitment complete."
    )


class AcceptIAmAction(BaseActionModel):
    params: AcceptIAmParams = Field(
        ...,
        description="Parameters for marking an identity as i_am_statement complete.",
    )


class AcceptIdentityVisualizationAction(BaseActionModel):
    params: AcceptIdentityVisualizationParams = Field(
        ..., description="Parameters for marking an identity as visualization complete."
    )


class ArchiveIdentityAction(BaseActionModel):
    params: ArchiveIdentityParams = Field(
        ..., description="Parameters for archiving an identity."
    )


class NestIdentityAction(BaseActionModel):
    params: NestIdentityParams = Field(
        ..., description="Parameters for nesting an identity under a parent identity."
    )


class TransitionPhaseAction(BaseActionModel):
    params: TransitionPhaseParams = Field(
        ..., description="Parameters for transitioning the coaching phase."
    )


class AddIdentityNoteAction(BaseActionModel):
    params: AddIdentityNoteParams = Field(
        ..., description="Parameters for adding a note to an identity."
    )


class SkipIdentityCategoryAction(BaseActionModel):
    params: SkipIdentityCategoryParams = Field(
        ..., description="Parameters for skipping an identity category."
    )


class UpdateWhoYouAreAction(BaseActionModel):
    params: UpdateWhoYouAreParams = Field(
        ..., description="Parameters for updating 'who you are' identities."
    )


class UpdateWhoYouWantToBeAction(BaseActionModel):
    params: UpdateWhoYouWantToBeParams = Field(
        ..., description="Parameters for updating 'who you want to be' identities."
    )


class UnskipIdentityCategoryAction(BaseActionModel):
    params: UnskipIdentityCategoryParams = Field(
        ..., description="Parameters for unskipping an identity category."
    )


class AddUserNoteAction(BaseActionModel):
    params: AddUserNoteParams = Field(
        description="Parameters for adding a note (or notes) to the users notes."
    )


class UpdateUserNoteAction(BaseActionModel):
    params: UpdateUserNoteParams = Field(
        ..., description="Parameters for updating user notes by id."
    )


class DeleteUserNoteAction(BaseActionModel):
    params: DeleteUserNoteParams = Field(
        ..., description="Parameters for deleting user notes by id."
    )


class UpdateAskedQuestionsAction(BaseActionModel):
    params: UpdateAskedQuestionsParams = Field(
        ..., description="Parameters for updating asked questions list."
    )


class ShowIntroductionCannedResponseComponentAction(BaseActionModel):
    params: ShowIntroductionCannedResponseComponentParams = Field(
        ..., description="Parameters for showing the canned response component."
    )


class ShowAcceptIAMComponentAction(BaseActionModel):
    params: ShowAcceptIAMComponentParams = Field(
        ..., description="Parameters for showing the accept 'I am' component."
    )


class ShowSuggestIAMStatementComponentAction(BaseActionModel):
    params: ShowSuggestIAMStatementComponentParams = Field(
        ..., description="Parameters for showing the suggest 'I am' statement component."
    )


class ShowIAmStatementsSummaryComponentAction(BaseActionModel):
    params: ShowIAmStatementsSummaryComponentParams = Field(
        ..., description="Parameters for showing the I Am statements summary component."
    )


class ShowCombineIdentitiesAction(BaseActionModel):
    params: ShowCombineIdentitiesParams = Field(
        ..., description="Parameters for showing the combine identities component."
    )


class CombineIdentitiesAction(BaseActionModel):
    params: CombineIdentitiesParams = Field(
        ..., description="Parameters for combining two identities."
    )


class PersistCombineIdentitiesAction(BaseActionModel):
    params: PersistCombineIdentitiesParams = Field(
        ..., description="Parameters for persisting the combine identities component."
    )


class PersistSuggestIAMStatementComponentAction(BaseActionModel):
    params: PersistSuggestIAMStatementComponentParams = Field(
        ...,
        description="Parameters for persisting the suggest 'I am' statement component.",
    )


class PersistIAmStatementsSummaryComponentAction(BaseActionModel):
    params: PersistIAmStatementsSummaryComponentParams = Field(
        ...,
        description="Parameters for persisting the I Am statements summary component.",
    )


class ShowNestIdentitiesAction(BaseActionModel):
    params: ShowNestIdentitiesParams = Field(
        ..., description="Parameters for showing the nest identities component."
    )


class PersistNestIdentitiesAction(BaseActionModel):
    params: PersistNestIdentitiesParams = Field(
        ..., description="Parameters for persisting the nest identities component."
    )


class ShowArchiveIdentityAction(BaseActionModel):
    params: ShowArchiveIdentityParams = Field(
        ..., description="Parameters for showing the archive identity component."
    )


class PersistArchiveIdentityAction(BaseActionModel):
    params: PersistArchiveIdentityParams = Field(
        ..., description="Parameters for persisting the archive identity component."
    )
