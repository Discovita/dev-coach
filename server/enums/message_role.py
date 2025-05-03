from django.db import models


# NOTE:
# The first value is the actual value stored in the database and used in your code. (.value)
# The second value is the human-readable label (display name) shown in forms, admin, etc. (.label)
class MessageRole(models.TextChoices):
    COACH = "coach", "Coach"
    USER = "user", "User"

    @classmethod
    def from_string(cls, value: str) -> "MessageRole":
        """
        Convert a string to a MessageRole enum value.
        """
        normalized = value.upper().replace(" ", "_").replace("-", "_")
        for member in cls:
            if member.name == normalized or member.value == normalized:
                return member
        valid_types = ", ".join([t.name for t in cls])
        raise ValueError(f"Unknown message role: {value}. Valid roles: {valid_types}")

    def __str__(self) -> str:
        """
        Get a human-readable string representation of the message role.
        """
        return self.label
