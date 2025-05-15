from typing import Optional, List
from pydantic import BaseModel, Field
from enums.identity_category import IdentityCategory


class PromptContext(BaseModel):
    """
    Context data used to format prompt templates for the coach chatbot.
    Used by the PromptManager and prompt formatting utilities.
    """

    user_name: Optional[str]
    recent_messages: Optional[str]  # this is a formatted list.
    identities: Optional[List[str]] = Field(default_factory=list)
    number_of_identities: Optional[int]
    current_identity_description: Optional[str] = None
