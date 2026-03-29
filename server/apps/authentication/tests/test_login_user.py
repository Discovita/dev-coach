"""
Integration tests for login_user function.
"""

from django.test import TestCase

from apps.authentication.functions.public import login_user
from apps.users.models import User


class LoginUserTests(TestCase):
    """Tests for the login_user function."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="login@example.com", password="TestPass1!"
        )

    def test_returns_user_id(self):
        """Result should contain the user's ID."""
        result = login_user(self.user)
        self.assertEqual(result["user_id"], self.user.id)

    def test_returns_jwt_tokens(self):
        """Result should contain valid refresh and access tokens."""
        result = login_user(self.user)
        self.assertIn("tokens", result)
        self.assertIn("refresh", result["tokens"])
        self.assertIn("access", result["tokens"])
        self.assertTrue(len(result["tokens"]["refresh"]) > 0)
        self.assertTrue(len(result["tokens"]["access"]) > 0)

    def test_tokens_differ_per_call(self):
        """Each call should produce fresh tokens."""
        result1 = login_user(self.user)
        result2 = login_user(self.user)
        self.assertNotEqual(result1["tokens"]["access"], result2["tokens"]["access"])
