"""
Permanently delete a user and everything hanging off them.

See: apps/users/functions/admin/__init__.py
"""

from apps.users.functions.admin.delete_user_media import (
    collect_user_media_keys,
    delete_media_keys,
)
from apps.users.models import User


def delete_user_account(user: User) -> None:
    """
    Delete ``user``, their stored files, and cascade to all of their data.

    Every model that points at a user does so with ``on_delete=CASCADE``
    (chat messages, actions, identities, coach state, breaks, meditations,
    reference images, user notes, identity image chat), so a single
    ``delete()`` clears the whole graph. The one exception is
    ``Invite.invited_by``, which is ``SET_NULL`` — invites this user sent
    survive with no sender, which is the intended behaviour: revoking an
    admin should not revoke the invitations they handed out.

    Storage keys are collected first, since the rows naming them are about
    to disappear, and the objects are removed after the database delete
    succeeds. Ordering it that way means a storage failure leaves orphaned
    files rather than files deleted out from under a user who still exists.

    Args:
        user: The user to delete.
    """
    media_keys = collect_user_media_keys(user)
    user.delete()
    delete_media_keys(media_keys)
