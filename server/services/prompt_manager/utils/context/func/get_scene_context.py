"""
Context function for building scene description from identity fields.
Formats identity scene data (clothing, mood, setting) for use in image generation prompts.
"""

from apps.identities.models import Identity
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


def get_scene_context(identity: Identity) -> str:
    """
    Build scene description from identity's clothing, mood, and setting fields.
    
    Takes the scene-specific fields from the Identity model and formats them into
    a structured string suitable for image generation prompts.
    
    Args:
        identity: The Identity model instance with scene fields
        
    Returns:
        String describing the scene elements in format:
        "CLOTHING: <clothing>
        MOOD/FEELING: <mood>
        SETTING: <setting>"
        Returns empty string if no scene fields are set.
    """
    log.debug(f"Building scene context for identity: {identity.name}")
    
    parts = []
    
    if identity.clothing:
        parts.append(f"CLOTHING: {identity.clothing}")
    
    if identity.mood:
        parts.append(f"MOOD/FEELING: {identity.mood}")
    
    if identity.setting:
        parts.append(f"SETTING: {identity.setting}")
    
    if not parts:
        log.debug("No scene fields set for identity")
        return ""
    
    scene_description = "\n".join(parts)
    log.debug(f"Generated scene context: {scene_description}")
    return scene_description
