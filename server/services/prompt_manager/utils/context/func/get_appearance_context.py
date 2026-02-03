"""
Context function for building appearance description from user preferences.
Formats user appearance data for use in image generation prompts.
"""

from apps.users.models import User
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


def get_appearance_context(user: User) -> str:
    """
    Build a natural language body description from user appearance preferences.
    
    Takes appearance fields from the User model and formats them into a descriptive
    string suitable for image generation prompts.
    
    Args:
        user: The User model instance with appearance preferences
        
    Returns:
        String describing the appearance, e.g., 
        "a tall athletic man with medium skin tone, brown hair, and blue eyes in their 30s"
        Returns empty string if no appearance preferences are set.
    """
    log.debug(f"Building appearance context for user: {user.email}")
    
    parts = []
    
    # Height
    if user.height:
        height_str = user.height.replace("_", " ")
        parts.append(height_str)
    
    # Build
    if user.build:
        parts.append(user.build)
    
    # Skin tone
    if user.skin_tone:
        skin_tone_str = user.skin_tone.replace("_", "-")
        parts.append(f"{skin_tone_str}-skinned")
    
    # Gender
    if user.gender:
        parts.append(user.gender)
    
    # Age range - format to natural language
    if user.age_range:
        age_mapping = {
            "twenties": "in their 20s",
            "thirties": "in their 30s",
            "forties": "in their 40s",
            "fifties": "in their 50s",
            "sixty_plus": "in their 60s",
        }
        age_str = age_mapping.get(user.age_range, user.age_range.replace("_", " "))
        parts.append(age_str)
    
    # Hair and eyes - combine with "with"
    hair_eye_parts = []
    if user.hair_color:
        hair_eye_parts.append(f"{user.hair_color} hair")
    if user.eye_color:
        hair_eye_parts.append(f"{user.eye_color} eyes")
    
    if hair_eye_parts:
        parts.append(f"with {' and '.join(hair_eye_parts)}")
    
    # Return empty string if no appearance data
    if not parts:
        log.debug("No appearance preferences set for user")
        return ""
    
    # Combine into natural language description
    description = "a " + " ".join(parts)
    log.debug(f"Generated appearance context: {description}")
    return description
