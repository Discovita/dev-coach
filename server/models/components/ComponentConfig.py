from typing import List, Literal, Union
from pydantic import BaseModel, Field


class CannedResponseButton(BaseModel):
    """
    Represents a single canned response button presented to the user.

    Used by: CannedResponseComponent.component_data.buttons

    Consumed in: `server/apps/coach/views.py` via component action handling
    and surfaced to the frontend through `CoachResponseSerializer` in
    `server/apps/coach/serializers.py`.
    """

    label: str = Field(
        ..., description="Button label shown to the user"
    )
    action: str = Field(
        ..., description="Name of the action to perform"
    )
    params: str = Field(
        ..., description="Parameters for the action to perform"
    )



class CannedResponseData(BaseModel):
    """
    Payload for the canned response component. Encapsulates the list of
    available canned response buttons.
    """

    buttons: List[CannedResponseButton] = Field(
        ..., description="List of canned response buttons"
    )


class CannedResponseComponent(BaseModel):
    """
    Strongly-typed model for the canned response component configuration.

    This model is intended to be embedded as the `component` field inside
    `server/models/CoachChatResponse.CoachChatResponse` so the frontend can
    render the appropriate UI with minimal custom logic.
    """

    component_type: Literal["canned_response"] = Field(
        "canned_response",
        description="Discriminator used by the frontend universal component renderer",
    )
    component_data: CannedResponseData = Field(
        ..., description="Typed data for the canned response component"
    )


# Discriminated union of all supported component configurations.
# Extend this union as new components are introduced.
ComponentConfig = Union[CannedResponseComponent]


