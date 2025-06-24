from pydantic import BaseModel, Field
from typing import List, Optional
from services.action_handler.models.actions import (
    AddUserNoteAction,
    UpdateUserNoteAction,
    DeleteUserNoteAction,
)


class SentinelChatResponse(BaseModel):
    """
    Response model for the Sentinel.
    Each field is an optional action, named after the action, and typed to the corresponding action model.
    """

    add_user_note: Optional[AddUserNoteAction] = Field(
        default=None, description="Perform the add_user_note action."
    )
    update_user_note: Optional[UpdateUserNoteAction] = Field(
        default=None, description="Perform the update_user_note action."
    )
    delete_user_note: Optional[DeleteUserNoteAction] = Field(
        default=None, description="Perform the delete_user_note action."
    )
