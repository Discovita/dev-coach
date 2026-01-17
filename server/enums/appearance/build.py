from django.db import models


class Build(models.TextChoices):
    """
    Enum for build/body type visualization options in image generation.
    """

    SLIM = "slim", "Slim"
    ATHLETIC = "athletic", "Athletic"
    AVERAGE = "average", "Average"
    STOCKY = "stocky", "Stocky"
    LARGE = "large", "Large"

    def __str__(self) -> str:
        """
        Get a human-readable string representation of the build.
        """
        return self.label
