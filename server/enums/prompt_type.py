from django.db import models


class PromptType(models.TextChoices):
    """
    Enum for the possible prompt types in the coaching system.
    Some prompts are not related at all to the coach (ie the sentinel)
    """

    COACH = "coach", "Coach"
    SENTINEL = "sentinel", "Sentinel"
    SYSTEM = "system", "System"
    IMAGE_GENERATION = "image_generation", "Image Generation"

    def get_all_actions() -> list:
        """Get all action types as a list."""
        return list(PromptType)

    @classmethod
    def from_string(cls, value: str) -> "PromptType":
        """
        Convert a string to an PromptType enum value, accepting flexible input.
        """
        normalized = value.lower().replace(" ", "_").replace("-", "_")
        for member in cls:
            if member.name.lower() == normalized or member.value.lower() == normalized:
                return member
        valid_types = ", ".join([t.name for t in cls])
        raise ValueError(f"Unknown action type: {value}. Valid types: {valid_types}")

    def __str__(self) -> str:
        """
        Get a human-readable string representation of the action type.
        """
        return self.label
