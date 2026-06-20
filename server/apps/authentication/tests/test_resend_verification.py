"""
Tests for the resend-verification flow (function + endpoint).
"""

from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from apps.authentication.functions.public import resend_verification
from apps.users.models import User

SEND_SEAM = (
    "apps.authentication.functions.public.resend_verification"
    ".send_verification_email"
)


class ResendVerificationFunctionTests(TestCase):
    """Tests for the resend_verification business function."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="resend@example.com", password="TestPass1!"
        )

    @patch(SEND_SEAM, return_value=True)
    def test_unverified_user_gets_email(self, mock_send):
        result = resend_verification("resend@example.com")
        mock_send.assert_called_once_with(self.user)
        self.assertTrue(result["email_sent"])

    @patch(SEND_SEAM, return_value=True)
    def test_already_verified_user_is_skipped(self, mock_send):
        self.user.is_email_verified = True
        self.user.save()
        result = resend_verification("resend@example.com")
        mock_send.assert_not_called()
        self.assertFalse(result["email_sent"])

    @patch(SEND_SEAM, return_value=True)
    def test_unknown_email_is_noop(self, mock_send):
        result = resend_verification("nobody@example.com")
        mock_send.assert_not_called()
        self.assertFalse(result["email_sent"])

    @patch(SEND_SEAM, return_value=True)
    def test_does_not_leak_user_existence(self, _mock_send):
        """Known and unknown emails return the same generic message."""
        known = resend_verification("resend@example.com")
        unknown = resend_verification("nobody@example.com")
        self.assertEqual(known["message"], unknown["message"])


class ResendVerificationEndpointTests(APITestCase):
    """Tests for POST /api/v1/auth/resend-verification/."""

    def setUp(self):
        self.url = "/api/v1/auth/resend-verification"
        self.user = User.objects.create_user(
            email="resend@example.com", password="TestPass1!"
        )

    def test_missing_email_returns_400(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch(SEND_SEAM, return_value=True)
    def test_valid_email_returns_success(self, _mock_send):
        response = self.client.post(
            self.url, {"email": "resend@example.com"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

    def test_unknown_email_returns_success(self):
        """Unknown email still returns 200 (no information leak)."""
        response = self.client.post(
            self.url, {"email": "nobody@example.com"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
