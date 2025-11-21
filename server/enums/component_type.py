from django.db import models


class ComponentType(models.TextChoices):
    """
    Enum for frontend-rendered component types in Coach responses.
    """

    INTRO_CANNED_RESPONSE = "intro_canned_response", "Intro Canned Response"
    WARMUP_IDENTITIES = "warmup_identities", "Warmup Identities"
    BRAINSTORMING_IDENTITIES = "brainstorming_identities", "Brainstorming Identities"
    COMBINE_IDENTITIES = "combine_identities", "Combine Identities"
    NEST_IDENTITIES = "nest_identities", "Nest Identities"
    ACCEPT_I_AM = "accept_i_am", "Accept I Am"

    @classmethod
    def from_string(cls, value: str) -> "ComponentType":
        """
        Convert a string to a ComponentType enum value, accepting flexible input.
        """
        normalized = value.lower().replace(" ", "_").replace("-", "_")
        for member in cls:
            if member.name.lower() == normalized or member.value.lower() == normalized:
                return member
        valid_types = ", ".join([t.name for t in cls])
        raise ValueError(
            f"Unknown component type: {value}. Valid types: {valid_types}"
        )

    def __str__(self) -> str:
        """
        Get a human-readable string representation of the component type.
        """
        return self.label

