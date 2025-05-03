from django.db import models


class CoachingState(models.TextChoices):
    """
    Enum for the possible coaching state in the coaching system.
    """

    INTRODUCTION = "introduction", "Introduction"
    IDENTITY_BRAINSTORMING = "identity_brainstorming", "Identity Brainstorming"
    IDENTITY_REFINEMENT = "identity_refinement", "Identity Refinement"

    @classmethod
    def from_string(cls, value: str) -> "CoachingState":
        """
        Convert a string to an CoachingState enum value, accepting flexible input.
        """
        normalized = value.lower().replace(" ", "_").replace("-", "_")
        for member in cls:
            if member.name.lower() == normalized or member.value.lower() == normalized:
                return member
        valid_types = ", ".join([t.name for t in cls])
        raise ValueError(
            f"Unknown identity category: {value}. Valid categories: {valid_types}"
        )

    def __str__(self) -> str:
        """
        Get a human-readable string representation of the identity category.
        """
        return self.label
