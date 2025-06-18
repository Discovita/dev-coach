from django.db import models


class ContextKey(models.TextChoices):
    """
    Enumeration of context keys.
    """

    USER_NAME = "user_name", "User Name"
    IDENTITIES = "identities", "Identities"
    NUMBER_OF_IDENTITIES = "number_of_identities", "Number of Identities"
    IDENTITY_FOCUS = "identity_focus", "Identity Focus"
    WHO_YOU_ARE = "who_you_are", "Who You Are"
    WHO_YOU_WANT_TO_BE = "who_you_want_to_be", "Who You Want to Be"
    FOCUSED_IDENTITIES = "focused_identities", "Focused Identities"
    USER_NOTES = "user_notes", "User Notes"
    CURRENT_MESSAGE = "current_message", "Current Message"
    PREVIOUS_MESSAGE = "previous_message", "Previous Message"

    @classmethod
    def from_string(cls, value: str) -> "ContextKey":
        """
        Convert a string to an ContextKey enum value, accepting flexible input.
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
        Get a human-readable string representation of the context key.
        """
        return self.label
