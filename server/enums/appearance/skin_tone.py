from django.db import models


class SkinTone(models.TextChoices):
    """
    Enum for skin tone options following Apple emoji convention.
    Used for appearance visualization in image generation.
    """

    LIGHT = "light", "Light"
    MEDIUM_LIGHT = "medium_light", "Medium-Light"
    MEDIUM = "medium", "Medium"
    MEDIUM_DARK = "medium_dark", "Medium-Dark"
    DARK = "dark", "Dark"

    def __str__(self) -> str:
        """
        Get a human-readable string representation of the skin tone.
        """
        return self.label
