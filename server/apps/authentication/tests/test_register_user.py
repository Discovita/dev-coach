"""
Integration tests for register_user function.
"""

from unittest.mock import patch

from django.test import TestCase

from apps.authentication.functions.public import register_user
from apps.users.models import User


class RegisterUserTests(TestCase):
    """Tests for the register_user function."""

    def setUp(self):
        # register_user sends a verification email via SES; mock the seam so
        # tests never touch the network.
        patcher = patch(
            "apps.authentication.functions.public.register_user"
            ".send_verification_email",
            return_value=True,
        )
        self.mock_send_verification = patcher.start()
        self.addCleanup(patcher.stop)

    def test_sends_verification_email(self):
        """Registration should trigger a verification email (best-effort)."""
        register_user(email="verify@example.com", password="TestPass1!")
        user = User.objects.get(email="verify@example.com")
        self.mock_send_verification.assert_called_once_with(user)

    def test_new_user_is_unverified(self):
        """A freshly registered user starts unverified."""
        register_user(email="unverified@example.com", password="TestPass1!")
        user = User.objects.get(email="unverified@example.com")
        self.assertFalse(user.is_email_verified)

    def test_creates_user_in_database(self):
        """Should create a User row with the given email."""
        register_user(email="new@example.com", password="TestPass1!")
        self.assertTrue(User.objects.filter(email="new@example.com").exists())

    def test_returns_user_id(self):
        """Result should contain the new user's ID."""
        result = register_user(email="new@example.com", password="TestPass1!")
        user = User.objects.get(email="new@example.com")
        self.assertEqual(result["user_id"], user.id)

    def test_returns_jwt_tokens(self):
        """Result should contain refresh and access tokens."""
        result = register_user(email="new@example.com", password="TestPass1!")
        self.assertIn("tokens", result)
        self.assertIn("refresh", result["tokens"])
        self.assertIn("access", result["tokens"])
        self.assertTrue(len(result["tokens"]["refresh"]) > 0)
        self.assertTrue(len(result["tokens"]["access"]) > 0)

    def test_password_is_hashed(self):
        """Stored password should be hashed, not plaintext."""
        register_user(email="new@example.com", password="TestPass1!")
        user = User.objects.get(email="new@example.com")
        self.assertNotEqual(user.password, "TestPass1!")
        self.assertTrue(user.check_password("TestPass1!"))

    def test_duplicate_email_raises(self):
        """Creating a user with an existing email should raise."""
        register_user(email="dupe@example.com", password="TestPass1!")
        with self.assertRaises(Exception):
            register_user(email="dupe@example.com", password="TestPass1!")
