from typing import Optional, List
from pydantic import BaseModel, Field
from enums.identity_category import IdentityCategory


class PromptContext(BaseModel):
    """
    Context data used to format prompt templates for the coach chatbot.
    Used by the PromptManager and prompt formatting utilities.
    """

    user_name: Optional[str]
    user_goals: Optional[List[str]]
    recent_messages: Optional[str]  # this is a formatted list.
    identities: Optional[List[str]] = Field(default_factory=list)
    number_of_identities: Optional[int]
    current_identity_description: Optional[str] = None
    current_focus: Optional[IdentityCategory] = None

    def format_goals(self) -> str:
        """
        Format goals as comma-separated string.
        """
        return ", ".join(self.user_goals)
