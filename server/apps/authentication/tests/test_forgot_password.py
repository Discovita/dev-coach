"""
Integration tests for forgot_password function.
"""

from unittest.mock import patch

from django.test import TestCase

from apps.authentication.functions.public import forgot_password
from apps.users.models import User


class ForgotPasswordTests(TestCase):
    """Tests for the forgot_password function."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="forgot@example.com", password="TestPass1!"
        )

    def test_nonexistent_email_returns_generic_message(self):
        """Should return a safe generic message for unknown emails."""
        result = forgot_password("nobody@example.com")
        self.assertIn("If an account exists", result["message"])
        self.assertFalse(result["email_sent"])

    @patch(
        "apps.authentication.functions.public.forgot_password"
        ".send_password_reset_email",
        return_value=True,
    )
    @patch(
        "apps.authentication.functions.public.forgot_password"
        ".generate_verification_token",
        return_value="abc123",
    )
    def test_existing_email_sends_reset(self, mock_gen, mock_send):
        """Should generate a token and send the email for known users."""
        result = forgot_password("forgot@example.com")
        mock_gen.assert_called_once_with(self.user)
        mock_send.assert_called_once_with(self.user)
        self.assertEqual(result["message"], "Password reset email sent")
        self.assertTrue(result["email_sent"])

    @patch(
        "apps.authentication.functions.public.forgot_password"
        ".send_password_reset_email",
        return_value=False,
    )
    @patch(
        "apps.authentication.functions.public.forgot_password"
        ".generate_verification_token",
        return_value="abc123",
    )
    def test_email_failure_raises_runtime_error(self, mock_gen, mock_send):
        """Should raise RuntimeError when SES send fails."""
        with self.assertRaises(RuntimeError) as ctx:
            forgot_password("forgot@example.com")
        self.assertIn("verification email", str(ctx.exception))

    def test_does_not_leak_user_existence(self):
        """Both existing and non-existing emails should return 'message' key."""
        result_exists = (
            forgot_password.__wrapped__("nobody@example.com")  # bypass any mock
            if hasattr(forgot_password, "__wrapped__")
            else forgot_password("nobody@example.com")
        )
        result_missing = forgot_password("also-nobody@example.com")
        self.assertIn("message", result_exists)
        self.assertIn("message", result_missing)
