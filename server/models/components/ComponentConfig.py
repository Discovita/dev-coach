from typing import List, Optional
from pydantic import BaseModel, Field


class Action(BaseModel):
    """
    Represents a single action to be performed.
    Used to define what happens when a button is clicked.
    """

    action: str = Field(..., description="The action type to perform")
    params: dict = Field(..., description="Parameters for the action")


class ComponentButton(BaseModel):
    """
    Represents a single button presented to the user.
    Contains a list of actions to be performed when the button is clicked.
    """

    label: str = Field(..., description="Button label shown to the user")
    actions: Optional[List[Action]] = Field(
        ..., description="List of actions to perform when this button is clicked"
    )


class ComponentConfig(BaseModel):
    """
    Configuration for frontend components. The frontend will determine
    how to render based on the structure of the data.
    """

    buttons: List[ComponentButton] = Field(
        ..., description="List of buttons to display"
    )
