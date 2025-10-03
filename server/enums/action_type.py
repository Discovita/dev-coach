from django.db import models


class ActionType(models.TextChoices):
    """
    Enum for the possible coach actions in the coaching system.
    """

    CREATE_IDENTITY = "create_identity", "Create Identity"
    UPDATE_IDENTITY = "update_identity", "Update Identity"
    UPDATE_IDENTITY_NAME = "update_identity_name", "Update Identity Name"
    UPDATE_IDENTITY_AFFIRMATION = (
        "update_identity_affirmation",
        "Update Identity Affirmation",
    )
    UPDATE_IDENTITY_VISUALIZATION = (
        "update_identity_visualization",
        "Update Identity Visualization",
    )
    ACCEPT_IDENTITY = "accept_identity", "Accept Identity"
    ACCEPT_IDENTITY_REFINEMENT = (
        "accept_identity_refinement",
        "Accept Identity Refinement",
    )
    ACCEPT_IDENTITY_AFFIRMATION = (
        "accept_identity_affirmation",
        "Accept Identity Affirmation",
    )
    ACCEPT_IDENTITY_VISUALIZATION = (
        "accept_identity_visualization",
        "Accept Identity Visualization",
    )
    ADD_IDENTITY_NOTE = "add_identity_note", "Add Identity Note"
    TRANSITION_PHASE = "transition_phase", "Transition Phase"
    SELECT_IDENTITY_FOCUS = "select_identity_focus", "Select Identity Focus"
    SKIP_IDENTITY_CATEGORY = "skip_identity_category", "Skip Identity Category"
    UNSKIP_IDENTITY_CATEGORY = "unskip_identity_category", "Unskip Identity Category"
    UPDATE_WHO_YOU_ARE = "update_who_you_are", "Update Who You Are"
    UPDATE_WHO_YOU_WANT_TO_BE = "update_who_you_want_to_be", "Update Who You Want to Be"
    UPDATE_ASKED_QUESTIONS = "update_asked_questions", "Update Asked Questions"
    SET_CURRENT_IDENTITY = "set_current_identity", "Set Current Identity"
    ADD_USER_NOTE = "add_user_note", "Add User Note"
    UPDATE_USER_NOTE = "update_user_note", "Update User Note"
    DELETE_USER_NOTE = "delete_user_note", "Delete User Note"
    SHOW_INTRODUCTION_CANNED_RESPONSE_COMPONENT = "show_introduction_canned_response_component", "Show Introduction Canned Response Component"
    SHOW_ACCEPT_I_AM_COMPONENT = "show_accept_i_am_component", "Show Accept I Am Component"
    SHOW_WARMUP_TEXT_COMPONENT = "show_warmup_text_component", "Show Warmup Text Component"

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
