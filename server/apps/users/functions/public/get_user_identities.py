"""
Get user identities with archive filtering.

This function retrieves identities for a user with optional archive state filtering.
"""

from typing import List
from django.db.models import QuerySet

from apps.users.models import User
from apps.identities.models import Identity
from enums.identity_state import IdentityState


def get_user_identities(
    user: User,
    include_archived: bool = False,
    archived_only: bool = False,
) -> QuerySet[Identity]:
    """
    Get identities for a user with optional archive filtering.

    Args:
        user: The user whose identities to retrieve
        include_archived: If True, include archived identities in results
        archived_only: If True, return only archived identities

    Returns:
        QuerySet of Identity objects matching the filter criteria

    Examples:
        >>> identities = get_user_identities(user)  # Excludes archived
        >>> all_identities = get_user_identities(user, include_archived=True)
        >>> archived = get_user_identities(user, archived_only=True)
    """
    queryset = Identity.objects.filter(user=user)

    if archived_only:
        return queryset.filter(state=IdentityState.ARCHIVED)
    elif not include_archived:
        return queryset.exclude(state=IdentityState.ARCHIVED)
    else:
        return queryset

