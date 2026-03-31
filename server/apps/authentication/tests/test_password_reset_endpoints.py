"""
Endpoint tests for forgot-password and reset-password flows.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from apps.authentication.utils.verification_token import TOKEN_EXPIRY_HOURS
from apps.users.models import User


class ForgotPasswordEndpointTests(APITestCase):
    """Tests for POST /api/v1/auth/forgot-password/."""

    def setUp(self):
        self.url = "/api/v1/auth/forgot-password"
        self.user = User.objects.create_user(
            email="forgot@example.com", password="TestPass1!"
        )

    def test_missing_email_returns_400(self):
        """Request without email should return 400."""
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch(
        "apps.authentication.functions.public.forgot_password"
        ".send_password_reset_email",
        return_value=True,
    )
    @patch(
        "apps.authentication.functions.public.forgot_password"
        ".generate_verification_token",
        return_value="tok",
    )
    def test_existing_email_returns_success(self, _mock_gen, _mock_send):
        """Known email should return 200 with success message."""
        response = self.client.post(
            self.url, {"email": "forgot@example.com"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

    def test_nonexistent_email_returns_success(self):
        """Unknown email should still return 200 (no information leak)."""
        response = self.client.post(
            self.url, {"email": "nobody@example.com"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

    @patch(
        "apps.authentication.functions.public.forgot_password"
        ".send_password_reset_email",
        return_value=False,
    )
    @patch(
        "apps.authentication.functions.public.forgot_password"
        ".generate_verification_token",
        return_value="tok",
    )
    def test_email_send_failure_returns_400(self, _mock_gen, _mock_send):
        """SES failure should return 400."""
        response = self.client.post(
            self.url, {"email": "forgot@example.com"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ResetPasswordEndpointTests(APITestCase):
    """Tests for POST /api/v1/auth/reset-password/."""

    def setUp(self):
        self.url = "/api/v1/auth/reset-password"
        self.user = User.objects.create_user(
            email="reset@example.com", password="OldPass1!"
        )
        self.user.verification_token = "valid-reset-token"
        self.user.email_verification_sent_at = datetime.now(tz=timezone.utc)
        self.user.save()

    def test_valid_token_resets_password(self):
        """Valid token and new password should return 200."""
        response = self.client.post(
            self.url,
            {"token": "valid-reset-token", "password": "NewPass1!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPass1!"))

    def test_missing_token_returns_400(self):
        """Request without token should return 400."""
        response = self.client.post(self.url, {"password": "NewPass1!"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_password_returns_400(self):
        """Request without password should return 400."""
        response = self.client.post(
            self.url, {"token": "valid-reset-token"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_token_returns_400(self):
        """Non-existent token should return 400."""
        response = self.client.post(
            self.url,
            {"token": "bogus-token", "password": "NewPass1!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expired_token_returns_400(self):
        """Expired token should return 400 and leave password unchanged."""
        self.user.email_verification_sent_at = datetime.now(
            tz=timezone.utc
        ) - timedelta(hours=TOKEN_EXPIRY_HOURS + 1)
        self.user.save()

        response = self.client.post(
            self.url,
            {"token": "valid-reset-token", "password": "NewPass1!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("OldPass1!"))
