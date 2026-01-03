"""
Context function for image generation prompts.
Formats identity data for use in Gemini image generation.
"""

from apps.identities.models import Identity
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


def get_identity_context_for_image(identity: Identity) -> str:
    """
    Format identity data for image generation prompts.

    Unlike get_current_identity_context which uses CoachState,
    this takes an Identity directly for image generation use cases.

    Args:
        identity: The Identity model instance to format

    Returns:
        Formatted string with identity details for image generation
    """
    log.debug(f"Formatting identity for image: {identity.name}")

    parts = [
        f'Identity Name: "{identity.name}"',
        f"Category: {identity.category}",
    ]

    if identity.i_am_statement:
        parts.append(f"I Am Statement: {identity.i_am_statement}")

    if identity.visualization:
        parts.append(f"Visualization: {identity.visualization}")

    if identity.notes:
        notes_str = "; ".join(identity.notes)
        parts.append(f"Notes: {notes_str}")

    return "\n".join(parts)

