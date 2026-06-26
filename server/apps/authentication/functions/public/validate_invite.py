"""
validate_invite

Look up an invite token and confirm it can still be accepted.
"""

from apps.authentication.models import Invite
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


class InviteInvalidError(Exception):
    """Raised when the token does not match any invite."""


class InviteExpiredError(Exception):
    """Raised when the invite has expired."""


class InviteAcceptedError(Exception):
    """Raised when the invite has already been used to create an account."""


def get_valid_invite(token: str) -> Invite:
    """
    Return the pending ``Invite`` for ``token`` or raise.

    Raises:
        InviteInvalidError: No invite matches the token.
        InviteAcceptedError: The invite was already accepted.
        InviteExpiredError: The invite has expired.
    """
    try:
        invite = Invite.objects.get(token=token)
    except Invite.DoesNotExist:
        log.warning("Invite lookup with invalid token")
        raise InviteInvalidError("This invite link is invalid.")

    if invite.is_accepted:
        log.info("Invite for %s already accepted", invite.email)
        raise InviteAcceptedError("This invite has already been used.")

    if invite.is_expired:
        log.info("Invite for %s has expired", invite.email)
        raise InviteExpiredError("This invite link has expired.")

    return invite


def validate_invite(token: str) -> dict:
    """
    Validate an invite token for the public locked-email register form.

    Returns:
        Dict with ``email`` so the UI can pre-fill and lock the field.
    """
    invite = get_valid_invite(token)
    return {"email": invite.email}
