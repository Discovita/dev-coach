from typing import List
from apps.identities.models import Identity


def format_identity_ids(identities: List[Identity]) -> str:
    """
    Format a list of Identity objects as a simple name-ID mapping.
    Returns a concise list showing only identity name and ID.
    """
    if not identities:
        return "No identities found."
    
    formatted = []
    for identity in identities:
        formatted.append(f"- **{identity.name}**: {identity.id} ({identity.state})")
    
    return "\n".join(formatted)

