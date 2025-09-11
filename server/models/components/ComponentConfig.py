from typing import List, Optional
from pydantic import BaseModel, Field


class ComponentButton(BaseModel):
    """
    Represents a single button presented to the user.
    Action and params are optional. If they are not provided, the button will send the message as if the user typed it. The label will be sent as the message.
    """

    label: str = Field(
        ..., description="Button label shown to the user (also used as the message)"
    )
    action: Optional[str] = Field(
        default=None,
        description="Optional action to perform (not needed for simple message sending)",
    )
    params: Optional[dict] = Field(
        default=None,
        description="Optional parameters for the action (not needed for simple message sending)",
    )


class ComponentConfig(BaseModel):
    """
    Configuration for frontend components. The frontend will determine
    how to render based on the structure of the data.
    """

    buttons: List[ComponentButton] = Field(
        ..., description="List of buttons to display"
    )
