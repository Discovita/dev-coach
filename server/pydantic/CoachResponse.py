from pydantic import BaseModel, Field
from typing import List, Optional


class CoachResponse(BaseModel):
    """Response model for coach API."""

    message: str = Field(..., description="Coach's response message")
    coach_state: CoachState = Field(
        ..., description="Updated state of the coaching session"
    )
    final_prompt: str = Field(
        "", description="The final prompt used to generate the coach's response"
    )
    actions: Optional[List[Action]] = Field(description="Actions performed")