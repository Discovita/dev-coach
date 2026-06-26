"""
register_via_invite

Accept an invite: create a verified account, mark the invite spent, log in.
"""

from typing import Any

from rest_framework_simplejwt.tokens import RefreshToken

from django.db import transaction

from apps.authentication.functions.public.validate_invite import get_valid_invite
from apps.users.models import User
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


@transaction.atomic
def register_via_invite(token: str, password: str) -> dict[str, Any]:
    """
    Create a user from a valid invite and issue JWT tokens (logged in).

    The account is created already-verified: clicking the emailed magic link
    proves ownership of the address, so no separate email-verification step is
    needed. The invite is stamped accepted within the same transaction so it
    cannot be reused.

    Args:
        token: Invite token from the magic link.
        password: Validated password (strength checked by the serializer).

    Returns:
        Dict with ``user_id`` and ``tokens`` (refresh/access).

    Raises:
        InviteInvalidError / InviteExpiredError / InviteAcceptedError:
            Propagated from ``get_valid_invite`` (re-validated under the lock).
    """
    # Re-fetch under the transaction and row-lock so two concurrent submits
    # can't both create an account from the same invite.
    invite = get_valid_invite(token)
    invite = type(invite).objects.select_for_update().get(pk=invite.pk)

    user = User.objects.create_user(email=invite.email, password=password)
    user.is_email_verified = True
    user.save(update_fields=["is_email_verified"])

    invite.mark_accepted()
    invite.save(update_fields=["accepted_at", "updated_at"])

    refresh = RefreshToken.for_user(user)

    log.info("User %s registered via invite", invite.email)
    return {
        "user_id": user.id,
        "tokens": {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        },
    }
