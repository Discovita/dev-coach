from typing import List, Literal, Optional

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
    category: Optional[str] = Field(..., description="Category of the identity")
    i_am_statement: Optional[str] = Field(
        default=None, description="I Am statement for the identity"
    )


class ComponentConfig(BaseModel):
    """
    Configuration for frontend components. The frontend will determine
    how to render based on the structure of the data.
    """

    component_type: str = Field(
        ..., description="Type of component to display (ComponentType value)"
    )
    video_key: Optional[str] = Field(
        default=None,
        description=(
            "For SESSION_VIDEO components: the registry key (e.g. "
            "`welcome_session_intro`) identifying which video this card renders. "
            "Set by the server when constructing the card; never by the LLM."
        ),
    )
    video_name: Optional[str] = Field(
        default=None,
        description=(
            "For SESSION_VIDEO components: human-readable display name "
            "(e.g. 'Welcome'). Embedded by the server from `SESSION_VIDEOS` "
            "at construction so the frontend renders the card with no registry "
            "lookup. Persisted to the ChatMessage `component_config` so a "
            "chat refresh shows the same card."
        ),
    )
    video_url: Optional[str] = Field(
        default=None,
        description=(
            "For SESSION_VIDEO components: full HTTPS URL the player streams "
            "from. Resolved via `get_video_url(video_key)` at construction "
            "(joins the current env's S3 bucket with the registry's `s3_key`). "
            "Persisted to the ChatMessage `component_config` so historical "
            "rows replay against whichever bucket they were created in — "
            "note: if the bucket name ever changes, persisted rows still "
            "point at the old URL until rebuilt."
        ),
    )
    texts: Optional[List[ComponentText]] = Field(
        default=None,
        description="Optional list of text blocks to render before/after the coach message",
    )
    buttons: Optional[List[ComponentButton]] = Field(
        default=None, description="Optional list of buttons to display"
    )
    identities: Optional[List[ComponentIdentity]] = Field(
        default=None,
        description="Optional list of identities to display in the component",
    )
    # Coaching Phase Videos — SESSION_BREAK historical state.
    # When END_BREAK fires, the original SESSION_BREAK ChatMessage's
    # component_config is mutated to record the close (and strip the
    # I'm Ready button so historical rows can't redispatch). The
    # frontend branches on `closed` to render a compact
    # "Took a break · {duration}" display.
    closed: Optional[bool] = Field(
        default=None,
        description=(
            "For SESSION_BREAK components: True once the user has clicked "
            "I'm Ready (END_BREAK fired). Drives the historical compact "
            "rendering on the frontend."
        ),
    )
    started_at: Optional[str] = Field(
        default=None,
        description=(
            "For SESSION_BREAK components: ISO-8601 timestamp the break "
            "opened. Set when END_BREAK fires (copied from `Break.started_at`)."
        ),
    )
    ended_at: Optional[str] = Field(
        default=None,
        description=(
            "For SESSION_BREAK components: ISO-8601 timestamp the user "
            "clicked I'm Ready. Set when END_BREAK fires "
            "(copied from `Break.ended_at`)."
        ),
    )
