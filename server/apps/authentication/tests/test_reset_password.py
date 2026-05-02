"""
Integration tests for reset_password function.
"""

from datetime import datetime, timedelta, timezone

from django.test import TestCase

from apps.authentication.functions.public import reset_password
from apps.authentication.functions.public.reset_password import (
    TokenExpiredError,
    TokenInvalidError,
)
from apps.authentication.utils.verification_token import TOKEN_EXPIRY_HOURS
from apps.users.models import User


class ResetPasswordTests(TestCase):
    """Tests for the reset_password function."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="reset@example.com", password="OldPass1!"
        )
        self.user.verification_token = "valid-token-abc"
        self.user.email_verification_sent_at = datetime.now(tz=timezone.utc)
        self.user.save()

    def test_updates_password(self):
        """Should change the user's password."""
        reset_password("valid-token-abc", "NewPass1!")
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPass1!"))
        self.assertFalse(self.user.check_password("OldPass1!"))

    def test_clears_token_after_reset(self):
        """Token and timestamp should be cleared after successful reset."""
        reset_password("valid-token-abc", "NewPass1!")
        self.user.refresh_from_db()
        self.assertEqual(self.user.verification_token, "")
        self.assertIsNone(self.user.email_verification_sent_at)

    def test_returns_success_message(self):
        """Should return a dict with a success message."""
        result = reset_password("valid-token-abc", "NewPass1!")
        self.assertEqual(result["message"], "Password updated successfully")

    def test_invalid_token_raises(self):
        """Non-existent token should raise TokenInvalidError."""
        with self.assertRaises(TokenInvalidError):
            reset_password("does-not-exist", "NewPass1!")

    def test_expired_token_raises(self):
        """Expired token should raise TokenExpiredError."""
        self.user.email_verification_sent_at = datetime.now(
            tz=timezone.utc
        ) - timedelta(hours=TOKEN_EXPIRY_HOURS + 1)
        self.user.save()

        with self.assertRaises(TokenExpiredError):
            reset_password("valid-token-abc", "NewPass1!")

    def test_expired_token_does_not_change_password(self):
        """Password should remain unchanged if token is expired."""
        self.user.email_verification_sent_at = datetime.now(
            tz=timezone.utc
        ) - timedelta(hours=TOKEN_EXPIRY_HOURS + 1)
        self.user.save()

        with self.assertRaises(TokenExpiredError):
            reset_password("valid-token-abc", "NewPass1!")

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("OldPass1!"))
