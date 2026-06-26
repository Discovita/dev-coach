"""
Authentication models.

``Invite`` — an email-bound, magic-link invitation that gates registration.

An invite is created by a super admin for a specific email address. No
``User`` row exists until the invite is accepted: the invitee clicks the
emailed magic link (``{FRONTEND}/invite/{token}``), which proves ownership of
the address, and submits a password to create their verified account.

Expiry is the real invalidator (mirrors Alpha Anywhere's MagicLoginToken).
``accepted_at`` marks an invite as spent — a single account can only be created
from it once.
"""

import secrets
import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

INVITE_EXPIRY_DAYS = 7
TOKEN_BYTES = 32  # secrets.token_hex(32) -> 64 hex chars


def generate_invite_token() -> str:
    """Return a fresh, cryptographically secure invite token (64 hex chars)."""
    return secrets.token_hex(TOKEN_BYTES)


def default_invite_expiry():
    """Default expiry: ``INVITE_EXPIRY_DAYS`` from now."""
    return timezone.now() + timedelta(days=INVITE_EXPIRY_DAYS)


class Invite(models.Model):
    """
    An email-bound invitation to register.

    Fields:
    - email: address the invite was sent to; the register form locks to it.
    - token: 64-hex magic-link token (unique).
    - expires_at: invite is invalid after this (default 7 days).
    - accepted_at: when the account was created from this invite (null = pending).
    - invited_by: the admin who created the invite (null if they're deleted).
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique identifier for this object.",
    )
    email = models.EmailField(
        help_text="Email address this invite was sent to (locked on register).",
    )
    token = models.CharField(
        max_length=100,
        unique=True,
        default=generate_invite_token,
        help_text="Magic-link token (secrets.token_hex(32)).",
    )
    expires_at = models.DateTimeField(
        default=default_invite_expiry,
        help_text="Invite is invalid after this time.",
    )
    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When an account was created from this invite (null = pending).",
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sent_invites",
        help_text="Admin who created this invite.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["email"])]

    def __str__(self) -> str:
        state = "accepted" if self.is_accepted else "pending"
        return f"Invite({self.email}, {state})"

    @property
    def is_accepted(self) -> bool:
        """Whether an account has already been created from this invite."""
        return self.accepted_at is not None

    @property
    def is_expired(self) -> bool:
        """Whether the invite has passed its expiry."""
        return timezone.now() > self.expires_at

    @property
    def is_pending(self) -> bool:
        """Whether the invite can still be accepted (not spent, not expired)."""
        return not self.is_accepted and not self.is_expired

    def refresh_expiry(self) -> None:
        """Reset the expiry window (used when an invite is re-sent)."""
        self.expires_at = default_invite_expiry()

    def mark_accepted(self) -> None:
        """Stamp the invite as accepted (spent)."""
        self.accepted_at = timezone.now()
