from django.db import models


class Build(models.TextChoices):
    """
    Enum for build/body type visualization options in image generation.
    
    Contains all possible build values. The frontend filters which options
    to display based on the user's selected gender:
    - Male: slim, athletic, average, muscular, stocky, large
    - Female: petite, slim, athletic, average, curvy, full_figured
    - Neutral: slim, athletic, average, stocky, large, heavyset
    """

    # Shared across genders
    SLIM = "slim", "Slim"
    ATHLETIC = "athletic", "Athletic"
    AVERAGE = "average", "Average"
    STOCKY = "stocky", "Stocky"
    LARGE = "large", "Large"
    
    # Male-specific
    MUSCULAR = "muscular", "Muscular"
    
    # Female-specific
    PETITE = "petite", "Petite"
    CURVY = "curvy", "Curvy"
    FULL_FIGURED = "full_figured", "Full-Figured"
    
    # Neutral-specific
    HEAVYSET = "heavyset", "Heavyset"

    def __str__(self) -> str:
        """
        Get a human-readable string representation of the build.
        """
        return self.label


# Gender-specific build groupings for frontend filtering
# Order: smallest to largest
BUILDS_MALE = [
    Build.SLIM,
    Build.ATHLETIC,
    Build.AVERAGE,
    Build.MUSCULAR,
    Build.STOCKY,
    Build.LARGE,
]

BUILDS_FEMALE = [
    Build.PETITE,
    Build.SLIM,
    Build.ATHLETIC,
    Build.AVERAGE,
    Build.CURVY,
    Build.FULL_FIGURED,
]

BUILDS_NEUTRAL = [
    Build.SLIM,
    Build.ATHLETIC,
    Build.AVERAGE,
    Build.STOCKY,
    Build.LARGE,
    Build.HEAVYSET,
]
