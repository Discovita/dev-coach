"""
Permanently delete a user and everything hanging off them.

See: apps/users/functions/admin/__init__.py
"""

from apps.users.models import User


def delete_user_account(user: User) -> None:
    """
    Delete ``user`` and cascade to all of their data.

    Every model that points at a user does so with ``on_delete=CASCADE``
    (chat messages, actions, identities, coach state, breaks, meditations,
    reference images, user notes, identity image chat), so a single
    ``delete()`` clears the whole graph. The one exception is
    ``Invite.invited_by``, which is ``SET_NULL`` — invites this user sent
    survive with no sender, which is the intended behaviour: revoking an
    admin should not revoke the invitations they handed out.

    Files already written to S3 for this user's reference and generated
    images are not removed; only the rows referencing them are.

    Args:
        user: The user to delete.
    """
    user.delete()
