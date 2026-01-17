from django.db import models


class AgeRange(models.TextChoices):
    """
    Enum for age range visualization options in image generation.
    """

    TWENTIES = "twenties", "Young Adult (20s)"
    THIRTIES = "thirties", "In Their 30s"
    FORTIES = "forties", "In Their 40s"
    FIFTIES = "fifties", "Middle-Aged (50s)"
    SIXTY_PLUS = "sixty_plus", "Mature (60+)"

    def __str__(self) -> str:
        """
        Get a human-readable string representation of the age range.
        """
        return self.label
