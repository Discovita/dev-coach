"""
Integration tests for register_user function.
"""

from django.test import TestCase

from apps.authentication.functions.public import register_user
from apps.users.models import User


class RegisterUserTests(TestCase):
    """Tests for the register_user function."""

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
