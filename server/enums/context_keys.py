from django.db import models


class ContextKey(models.TextChoices):
    """
    Enumeration of context keys.
    """

    # TODO: Need to add remaining keys to this list for the other prompts
    # TODO: Talk to Leigh Ann about what other context variables are needed
    USER_NAME = "user_name", "User Name"
    RECENT_MESSAGES = "recent_messages", "Recent Messages"
    IDENTITIES = "identities", "Identities"
    NUMBER_OF_IDENTITIES = "number_of_identities", "Number of Identities"

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
