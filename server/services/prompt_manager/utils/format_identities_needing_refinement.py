from typing import List
from apps.identities.models import Identity


def format_identities_needing_refinement(identities: List[Identity]) -> str:
    """
    Format a list of Identity objects that are not refinement_complete as a simple markdown list.
    The intent is simply to provide a simple list of identities that need refinement to the Coach so it knows whats next. No details needed here. 
    """
    if not identities:
        return "No identities found."
    
    formatted = []
    formatted.append("## Identities Needing Refinement")
    for identity in identities:
        formatted.append(f"- {identity.name} ({identity.get_category_display()})")
    
    return "\n".join(formatted)
