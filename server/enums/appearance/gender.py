from django.db import models


class Gender(models.TextChoices):
    """
    Enum for gender visualization options in image generation.
    """

    MAN = "man", "Man"
    WOMAN = "woman", "Woman"
    PERSON = "person", "Person"  # Gender neutral

    def __str__(self) -> str:
        """
        Get a human-readable string representation of the gender.
        """
        return self.label
