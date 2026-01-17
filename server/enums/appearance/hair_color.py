from django.db import models


class HairColor(models.TextChoices):
    """
    Enum for hair color options in image generation.
    """

    BLACK = "black", "Black"
    BROWN = "brown", "Brown"
    BLONDE = "blonde", "Blonde"
    RED = "red", "Red"
    AUBURN = "auburn", "Auburn"
    GRAY = "gray", "Gray"
    WHITE = "white", "White"
    BALD = "bald", "Bald"

    def __str__(self) -> str:
        """
        Get a human-readable string representation of the hair color.
        """
        return self.label
