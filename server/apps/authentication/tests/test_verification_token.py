"""
Unit tests for verification token utilities.
"""

from datetime import datetime, timedelta, timezone

from django.test import TestCase

from apps.authentication.utils.verification_token import (
    TOKEN_EXPIRY_HOURS,
    generate_verification_token,
    is_token_expired,
)
from apps.users.models import User


class GenerateVerificationTokenTests(TestCase):
    """Tests for generate_verification_token."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="token@example.com", password="TestPass1!"
        )

    def test_returns_hex_string(self):
        """Should return a 64-character hex string (32 bytes)."""
        token = generate_verification_token(self.user)
        self.assertEqual(len(token), 64)
        int(token, 16)  # raises ValueError if not valid hex

    def test_persists_token_on_user(self):
        """Token and timestamp should be saved to the database."""
        token = generate_verification_token(self.user)
        self.user.refresh_from_db()

        self.assertEqual(self.user.verification_token, token)
        self.assertIsNotNone(self.user.email_verification_sent_at)

    def test_generates_unique_tokens(self):
        """Successive calls should produce different tokens."""
        token1 = generate_verification_token(self.user)
        token2 = generate_verification_token(self.user)
        self.assertNotEqual(token1, token2)

    def test_updates_sent_at_timestamp(self):
        """Timestamp should be refreshed on each call."""
        generate_verification_token(self.user)
        self.user.refresh_from_db()
        first_ts = self.user.email_verification_sent_at

        generate_verification_token(self.user)
        self.user.refresh_from_db()
        second_ts = self.user.email_verification_sent_at

        self.assertGreaterEqual(second_ts, first_ts)


class IsTokenExpiredTests(TestCase):
    """Tests for is_token_expired."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="expiry@example.com", password="TestPass1!"
        )

    def test_expired_when_no_timestamp(self):
        """Should return True when email_verification_sent_at is None."""
        self.user.email_verification_sent_at = None
        self.user.save()
        self.assertTrue(is_token_expired(self.user))

    def test_not_expired_when_recent(self):
        """Token generated just now should not be expired."""
        self.user.email_verification_sent_at = datetime.now(tz=timezone.utc)
        self.user.save()
        self.assertFalse(is_token_expired(self.user))

    def test_expired_after_24_hours(self):
        """Token older than TOKEN_EXPIRY_HOURS should be expired."""
        self.user.email_verification_sent_at = datetime.now(
            tz=timezone.utc
        ) - timedelta(hours=TOKEN_EXPIRY_HOURS + 1)
        self.user.save()
        self.assertTrue(is_token_expired(self.user))

    def test_not_expired_just_before_cutoff(self):
        """Token at 23 hours should still be valid."""
        self.user.email_verification_sent_at = datetime.now(
            tz=timezone.utc
        ) - timedelta(hours=TOKEN_EXPIRY_HOURS - 1)
        self.user.save()
        self.assertFalse(is_token_expired(self.user))
