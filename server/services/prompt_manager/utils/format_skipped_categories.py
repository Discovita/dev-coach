from typing import List
from enums.identity_category import IdentityCategory

def format_skipped_categories(skipped: List[str]) -> str:
    """
    Format a list of skipped identity category values as a markdown string.
    """
    if not skipped:
        return ""
    skipped_labels = []
    for cat in skipped:
        try:
            skipped_labels.append(IdentityCategory.from_string(cat).label)
        except Exception:
            skipped_labels.append(str(cat))
    return (
        "\n\n---\n\n" +
        "**Skipped Identity Categories:**\n" +
        "\n".join([f"- {label}" for label in skipped_labels])
    ) 