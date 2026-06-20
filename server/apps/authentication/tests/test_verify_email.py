"""
Tests for the email-verification flow (function + endpoint).
"""

from datetime import datetime, timedelta, timezone

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from apps.authentication.functions.public.verify_email import (
    VerificationExpiredError,
    VerificationInvalidError,
    verify_email,
)
from apps.authentication.utils.verification_token import TOKEN_EXPIRY_HOURS
from apps.users.models import User


class VerifyEmailFunctionTests(TestCase):
    """Tests for the verify_email business function."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="verify@example.com", password="TestPass1!"
        )
        self.user.verification_token = "valid-verify-token"
        self.user.email_verification_sent_at = datetime.now(tz=timezone.utc)
        self.user.save()

    def test_valid_token_marks_verified_and_clears_token(self):
        result = verify_email("valid-verify-token")
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)
        self.assertEqual(self.user.verification_token, "")
        self.assertIsNone(self.user.email_verification_sent_at)
        self.assertIn("verified", result["message"].lower())

    def test_invalid_token_raises(self):
        with self.assertRaises(VerificationInvalidError):
            verify_email("does-not-exist")

    def test_expired_token_raises_and_stays_unverified(self):
        self.user.email_verification_sent_at = datetime.now(
            tz=timezone.utc
        ) - timedelta(hours=TOKEN_EXPIRY_HOURS + 1)
        self.user.save()
        with self.assertRaises(VerificationExpiredError):
            verify_email("valid-verify-token")
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_email_verified)


class VerifyEmailEndpointTests(APITestCase):
    """Tests for POST /api/v1/auth/verify-email/."""

    def setUp(self):
        self.url = "/api/v1/auth/verify-email"
        self.user = User.objects.create_user(
            email="verify@example.com", password="TestPass1!"
        )
        self.user.verification_token = "valid-verify-token"
        self.user.email_verification_sent_at = datetime.now(tz=timezone.utc)
        self.user.save()

    def test_valid_token_returns_success(self):
        response = self.client.post(
            self.url, {"token": "valid-verify-token"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)

    def test_missing_token_returns_400(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_token_returns_400(self):
        response = self.client.post(self.url, {"token": "bogus"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expired_token_returns_400(self):
        self.user.email_verification_sent_at = datetime.now(
            tz=timezone.utc
        ) - timedelta(hours=TOKEN_EXPIRY_HOURS + 1)
        self.user.save()
        response = self.client.post(
            self.url, {"token": "valid-verify-token"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
