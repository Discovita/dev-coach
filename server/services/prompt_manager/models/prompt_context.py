from typing import Optional
from pydantic import BaseModel


class PromptContext(BaseModel):
    """
    Context data used to format prompt templates for the coach chatbot.
    Used by the PromptManager and prompt formatting utilities.
    """

    user_name: Optional[str]
    recent_messages: Optional[str]
    identities: Optional[str]
    number_of_identities: Optional[int]
    identity_focus: Optional[str]
    who_you_are: Optional[str]
    who_you_want_to_be: Optional[str]
    focused_identities: Optional[str]
    user_notes: Optional[str]
    current_message: Optional[str]
    previous_message: Optional[str]
    current_phase: Optional[str]
    brainstorming_category_context: Optional[str]
    current_identity: Optional[str]
    asked_questions: Optional[str]
    refinement_identities: Optional[str]
    commitment_identities: Optional[str]
    i_am_identities: Optional[str]
    visualization_identities: Optional[str]
    identity_ids: Optional[str]
