from django.db import models


class Height(models.TextChoices):
    """
    Enum for height visualization options in image generation.
    """

    SHORT = "short", "Short"
    BELOW_AVERAGE = "below_average", "Below Average"
    AVERAGE = "average", "Average"
    ABOVE_AVERAGE = "above_average", "Above Average"
    TALL = "tall", "Tall"

    def __str__(self) -> str:
        """
        Get a human-readable string representation of the height.
        """
        return self.label
