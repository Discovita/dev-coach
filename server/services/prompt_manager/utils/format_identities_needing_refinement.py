from typing import List
from apps.identities.models import Identity


def format_identities_needing_refinement(identities: List[Identity]) -> str:
    """
    Format a list of Identity objects that are not refinement_complete as a numbered list.
    The list is ordered chronologically and must be refined in that exact order.
    """
    if not identities:
        return "No identities found."
    
    formatted = []
    formatted.append("## Identities Needing Refinement")
    formatted.append("")
    formatted.append("**IMPORTANT: These identities are listed in chronological order (oldest first) and MUST be refined in the exact order shown. Always work from the top of the list to the bottom.**")
    formatted.append("")
    for idx, identity in enumerate(identities, 1):
        formatted.append(f"{idx}. **{identity.name}** ({identity.get_category_display()})")
    
    return "\n".join(formatted)