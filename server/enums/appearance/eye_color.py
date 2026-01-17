from django.db import models


class EyeColor(models.TextChoices):
    """
    Enum for eye color options in image generation.
    """

    BROWN = "brown", "Brown"
    BLUE = "blue", "Blue"
    GREEN = "green", "Green"
    HAZEL = "hazel", "Hazel"
    GRAY = "gray", "Gray"
    AMBER = "amber", "Amber"

    def __str__(self) -> str:
        """
        Get a human-readable string representation of the eye color.
        """
        return self.label
