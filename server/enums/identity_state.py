from django.db import models

# IdentityState is used to represent the state of an identity in the coaching process.
# This enum is referenced in the Identity model (see apps/coach/models.py or similar).
class IdentityState(models.TextChoices):
    """
    Enum for the possible states of an identity in the coaching process.
    """
    PROPOSED = "proposed", "Proposed"
    ACCEPTED = "accepted", "Accepted"
    REFINEMENT_COMPLETE = "refinement_complete", "Refinement Complete"

    @classmethod
    def from_string(cls, value: str) -> "IdentityState":
        """
        Convert a string to an IdentityState enum value, accepting flexible input.
        """
        normalized = value.lower().replace(" ", "_").replace("-", "_")
        for member in cls:
            if member.name.lower() == normalized or member.value.lower() == normalized:
                return member
        valid_types = ", ".join([t.name for t in cls])
        raise ValueError(
            f"Unknown identity state: {value}. Valid states: {valid_types}"
        )

    def __str__(self) -> str:
        """
        Get a human-readable string representation of the identity state.
        """
        return self.label