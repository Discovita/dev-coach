"""
Reorder a user's identities.

Assigns the ascending ``order`` value to each identity based on its position
in ``ordered_ids``. Identity IDs are assumed to already be validated as
belonging to the user (see ReorderIdentitiesRequestSerializer).
"""

from django.db import transaction

from apps.identities.models import Identity
from apps.users.models import User


@transaction.atomic
def reorder_user_identities(user: User, ordered_ids: list) -> None:
    """
    Persist a new display order for the given user's identities.

    Args:
        user: The owner of the identities.
        ordered_ids: Identity IDs in the desired order (index 0 shown first).
                     Must all belong to ``user`` (validated upstream).

    Each identity's ``order`` is set to its index in ``ordered_ids``. IDs not
    present in the list are left untouched (ties break on created_at).
    """
    identities_by_id = {
        identity.id: identity
        for identity in Identity.objects.filter(user=user, id__in=ordered_ids)
    }

    to_update = []
    for index, identity_id in enumerate(ordered_ids):
        identity = identities_by_id.get(identity_id)
        if identity is None:
            continue
        identity.order = index
        to_update.append(identity)

    if to_update:
        Identity.objects.bulk_update(to_update, ["order"])
