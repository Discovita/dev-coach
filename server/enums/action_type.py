from django.db import models


class ActionType(models.TextChoices):
    """
    Enum for the possible coaching state in the coaching system.
    """

    CREATE_IDENTITY = "create_identity", "Create Identity"
    UPDATE_IDENTITY = "update_identity", "Update Identity"
    ACCEPT_IDENTITY = "accept_identity", "Accept Identity"
    ACCEPT_IDENTITY_REFINEMENT = (
        "accept_identity_refinement",
        "Accept Identity Refinement",
    )
    ADD_IDENTITY_NOTE = "add_identity_note", "Add Identity Note"
    TRANSITION_STATE = "transition_state", "Transition State"
    SELECT_IDENTITY_FOCUS = "select_identity_focus", "Select Identity Focus"
    SKIP_IDENTITY_CATEGORY = "skip_identity_category", "Skip Identity Category"

    def get_all_actions() -> list:
        """Get all action types as a list."""
        return list(ActionType)

    @classmethod
    def from_string(cls, value: str) -> "ActionType":
        """
        Convert a string to an ActionType enum value, accepting flexible input.
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
