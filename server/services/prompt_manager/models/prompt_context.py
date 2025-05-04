from typing import Optional, List
from pydantic import BaseModel, Field
from enums.identity_state import IdentityState
from enums.identity_category import IdentityCategory

class IdentitySummary(BaseModel):
    """
    Summary of an identity for prompt context.
    Used in: PromptContext.identities_summary
    """
    id: str = Field(..., description="Unique identifier for the identity")
    description: str = Field(..., description="Description of the identity")
    state: IdentityState = Field(..., description="Current state of the identity")

class PromptContext(BaseModel):
    """
    Context data used to format prompt templates for the coach chatbot.
    Used by the PromptManager and prompt formatting utilities.
    """
    user_name: str
    user_goals: List[str]
    num_identities: int
    current_identity_description: Optional[str] = None
    identities_summary: List[IdentitySummary] = Field(default_factory=list, description="List of identity summaries")
    phase: str
    recent_messages: List[str] = []  # Recent conversation messages

    def format_goals(self) -> str:
        """
        Format goals as comma-separated string.
        """
        return ", ".join(self.user_goals)

    def format_identities(self) -> str:
        """
        Format identities summary as bulleted list with IDs.
        """
        if not self.identities_summary:
            return "No identities created yet."
        return "\n".join(
            f"- ID: {identity.id} | {identity.description} (state: {identity.state})"
            for identity in self.identities_summary
        )

    def user_summary(self) -> str:
        """
        Generate a summary of the user information.
        """
        return f"Name: {self.user_name}\nGoals: {self.format_goals()}"

    def format_recent_messages(self) -> str:
        """
        Format recent messages as a conversation.
        """
        if not self.recent_messages:
            return "No recent messages."
        return "\n".join(self.recent_messages)

    def format_identity_categories(self) -> str:
        """
        Format identity categories as a list of enum values.
        """
        return ", ".join([f"'{category.value}'" for category in IdentityCategory]) 