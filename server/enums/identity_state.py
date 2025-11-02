from django.db import models

# IdentityState is used to represent the state of an identity in the coaching process.
# This enum is referenced in the Identity model (see apps/coach/models.py or similar).
"""
Proposed: Every identity starts as proposed. 
Accepted: An identity is accepted when it makes it to the Identity Refinement Phase.
Refinement Complete: An identity is refinement complete when the user has refined it to their liking.
Commitment Complete: An identity is commitment complete when the user has committed to it and wants to advance to the I Am Statement Phase with it.
I Am Complete: An identity is i am complete when the user has created an i am statement for it.
Visualization Complete: An identity is visualization complete when the user has created a visualization for it.
"""


class IdentityState(models.TextChoices):
    """
    Enum for the possible states of an identity in the coaching process.
    """

    PROPOSED = "proposed", "Proposed"
    ACCEPTED = "accepted", "Accepted"
    REFINEMENT_COMPLETE = "refinement_complete", "Refinement Complete"
    COMMITMENT_COMPLETE = "commitment_complete", "Commitment Complete"
    I_AM_COMPLETE = "i_am_complete", "I Am Complete"
    VISUALIZATION_COMPLETE = "visualization_complete", "Visualization Complete"

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
