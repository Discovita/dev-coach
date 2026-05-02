"""
Compute the next version number for a new prompt.

See: apps/prompts/utils/__init__.py
"""

from typing import Optional

from apps.prompts.models import Prompt


def get_next_prompt_version(
    prompt_type: str, coaching_phase: Optional[str] = None
) -> int:
    """
    Return the next sequential version number for a prompt.

    Versions are scoped to (prompt_type, coaching_phase). When coaching_phase
    is None, the scope is (prompt_type, coaching_phase IS NULL).

    Args:
        prompt_type: The PromptType value.
        coaching_phase: The CoachingPhase value, or None.

    Returns:
        The next integer version (1 if no prior versions exist).
    """
    filters = {"prompt_type": prompt_type}
    if coaching_phase:
        filters["coaching_phase"] = coaching_phase
    else:
        filters["coaching_phase__isnull"] = True

    latest = Prompt.objects.filter(**filters).order_by("-version").first()
    return (latest.version + 1) if latest else 1
