from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class ComponentAction(BaseModel):
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
    actions: Optional[List[ComponentAction]] = Field(
        default=None,
        description="List of actions to perform when this button is clicked",
    )


class ComponentText(BaseModel):
    """
    Arbitrary markdown text to render with the coach message.
    - text: markdown content to render
    - location: whether to render before or after the coach message
    - source: label indicating where this text came from (e.g., "warmup")
    """

    text: str = Field(..., description="Markdown text to inject")
    location: Literal["before", "after"] = Field(
        ..., description="Where to render relative to the coach message"
    )
    source: str = Field(..., description="Source label for this text block")


class ComponentIdentity(BaseModel):
    """
    Represents a single identity for display in components.
    Contains the essential information needed to display an identity.
    """

    id: str = Field(..., description="Unique identifier for the identity")
    name: str = Field(..., description="Name of the identity")
    category: str = Field(..., description="Category of the identity")


class ComponentConfig(BaseModel):
    """
    Configuration for frontend components. The frontend will determine
    how to render based on the structure of the data.
    """

    texts: Optional[List[ComponentText]] = Field(
        default=None,
        description="Optional list of text blocks to render before/after the coach message",
    )
    buttons: List[ComponentButton] = Field(
        ..., description="List of buttons to display"
    )
    identities: Optional[List[ComponentIdentity]] = Field(
        default=None,
        description="Optional list of identities to display in the component",
    )
