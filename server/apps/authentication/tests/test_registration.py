"""
Endpoint tests for POST /api/v1/auth/register/.
"""

from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from apps.authentication.serializers import RegisterSerializer
from apps.users.models import User


class RegisterSerializerTests(TestCase):
    """Tests for RegisterSerializer validation."""

    def test_valid_input_passes(self):
        """Valid email and password should pass validation."""
        serializer = RegisterSerializer(
            data={"email": "ok@example.com", "password": "GoodPass1!"}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_weak_password_rejected(self):
        """Password failing strength check should be rejected."""
        serializer = RegisterSerializer(
            data={"email": "ok@example.com", "password": "weak"}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_duplicate_email_rejected(self):
        """Email already in use should be rejected."""
        User.objects.create_user(email="taken@example.com", password="Pass1!")
        serializer = RegisterSerializer(
            data={"email": "taken@example.com", "password": "GoodPass1!"}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_duplicate_email_case_insensitive(self):
        """Duplicate check should be case-insensitive."""
        User.objects.create_user(email="Taken@Example.com", password="Pass1!")
        serializer = RegisterSerializer(
            data={"email": "taken@example.com", "password": "GoodPass1!"}
        )
        self.assertFalse(serializer.is_valid())

    def test_missing_email_rejected(self):
        """Missing email should fail."""
        serializer = RegisterSerializer(data={"password": "GoodPass1!"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_missing_password_rejected(self):
        """Missing password should fail."""
        serializer = RegisterSerializer(data={"email": "ok@example.com"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_invalid_email_format_rejected(self):
        """Non-email string should fail."""
        serializer = RegisterSerializer(
            data={"email": "not-an-email", "password": "GoodPass1!"}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)


class RegisterEndpointTests(APITestCase):
    """Tests for the POST /api/v1/auth/register/ endpoint."""

    def setUp(self):
        self.url = "/api/v1/auth/register"
        self.valid_payload = {
            "email": "new@example.com",
            "password": "TestPass1!",
        }
        # Registration sends a verification email via SES; mock the seam.
        patcher = patch(
            "apps.authentication.functions.public.register_user"
            ".send_verification_email",
            return_value=True,
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_successful_registration(self):
        """Valid payload creates an unverified user and does NOT log them in."""
        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertNotIn("tokens", response.data)
        self.assertIn("user_id", response.data)
        user = User.objects.get(email="new@example.com")
        self.assertFalse(user.is_email_verified)

    def test_duplicate_email_returns_400(self):
        """Existing email should return 400."""
        User.objects.create_user(email="new@example.com", password="Pass1!")

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_weak_password_returns_400(self):
        """Weak password should return 400."""
        payload = {"email": "new@example.com", "password": "weak"}

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(User.objects.count(), 0)

    def test_missing_fields_returns_400(self):
        """Empty body should return 400."""
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
