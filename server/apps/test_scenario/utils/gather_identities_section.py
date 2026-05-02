"""
gather_identities_section

Gather all Identity objects for a user into a scenario template section list.
"""

from django.core.files.storage import default_storage

from apps.identities.models import Identity
from apps.test_scenario.utils.duplicate_s3_image import duplicate_s3_image


def gather_identities_section(user) -> list[dict]:
    """
    Build the ``identities`` template section from the user's live Identity records.

    Images are duplicated to new S3 keys so the template is self-contained and
    the original identity images remain unaffected.

    Args:
        user: The User model instance whose identities to capture.

    Returns:
        A list of identity dicts, each containing at minimum ``name`` and
        ``category``. Optional fields (``state``, ``i_am_statement``,
        ``visualization``, ``notes``, ``image``) are included only when present.
    """
    section: list[dict] = []
    for identity in Identity.objects.filter(user=user):
        entry: dict = {"name": identity.name, "category": identity.category}
        if identity.state:
            entry["state"] = identity.state
        if identity.i_am_statement:
            entry["i_am_statement"] = identity.i_am_statement
        if identity.visualization:
            entry["visualization"] = identity.visualization
        if identity.notes:
            entry["notes"] = identity.notes
        if identity.image:
            dup_key = duplicate_s3_image(identity.image)
            if dup_key:
                entry["image"] = default_storage.url(dup_key)
        section.append(entry)
    return section
