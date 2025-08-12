from django.db import models


class GetToKnowYouQuestions(models.TextChoices):
    """
    Enum for the possible questions that can be asked during the Get To Know You phase.
    """

    BACKGROUND_UPBRINGING = "background_upbringing", "Background/upbringing"
    FAMILY_STRUCTURE = "family_structure", "Family structure (siblings, parents, children, etc.)"
    WORK_LIVING = "work_living", "Work or what they do for a living"
    HOBBIES_INTERESTS = "hobbies_interests", "Hobbies or interests"
    WHY_HERE_HOPES = "why_here_hopes", "Why are you here? What do you hope to get out of this coaching?"

    @classmethod
    def from_string(cls, value: str) -> "GetToKnowYouQuestions":
        """
        Convert a string to a GetToKnowYouQuestions enum value, accepting flexible input.
        """
        normalized = value.lower().replace(" ", "_").replace("-", "_")
        for member in cls:
            if member.name.lower() == normalized or member.value.lower() == normalized:
                return member
        valid_types = ", ".join([t.name for t in cls])
        raise ValueError(
            f"Unknown get to know you question: {value}. Valid questions: {valid_types}"
        )

    def __str__(self) -> str:
        """
        Get a human-readable string representation of the question.
        """
        return self.label
