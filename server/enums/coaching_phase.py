from django.db import models


class CoachingPhase(models.TextChoices):
    """
    Enum for the possible coaching state in the coaching system.
    """

    # This was added so that we could control the content of the system_context sent to the LLM via the web interface. SYSTEM_CONTEXT is not a phase in the coaching process, but a context that is always sent to the LLM.
    SYSTEM_CONTEXT = "system_context", "System Context"
    INTRODUCTION = "introduction", "Introduction"
    GET_TO_KNOW_YOU = "get_to_know_you", "Get to Know You"
    IDENTITY_WARMUP = "identity_warm_up", "Identity Warm-Up"
    IDENTITY_BRAINSTORMING = "identity_brainstorming", "Identity Brainstorming"
    IDENTITY_REFINEMENT = "identity_refinement", "Identity Refinement"
    IDENTITY_AFFIRMATION = "identity_affirmation", "Identity Affirmation"
    IDENTITY_VISUALIZATION = "identity_visualization", "Identity Visualization"

    @classmethod
    def from_string(cls, value: str) -> "CoachingPhase":
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
