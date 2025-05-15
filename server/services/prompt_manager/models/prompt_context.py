from typing import Optional, List
from pydantic import BaseModel, Field


class PromptContext(BaseModel):
    """
    Context data used to format prompt templates for the coach chatbot.
    Used by the PromptManager and prompt formatting utilities.
    """
    user_name: Optional[str]
    recent_messages: Optional[str]  # this is a formatted list.
    identities: Optional[str]
    number_of_identities: Optional[int]
    identity_focus: Optional[str]
