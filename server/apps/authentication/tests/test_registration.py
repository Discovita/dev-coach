"""
Endpoint tests for POST /api/v1/auth/register/.
"""

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
    """
    The public self-service register endpoint is disabled (invite-only).

    Accounts can only be created by accepting an invite via
    ``/auth/register-via-invite`` (see test_invites.py). The endpoint stays
    mounted but refuses to create users, so the gate can't be bypassed by
    POSTing directly to the API even though the UI form is hidden.
    """

    def setUp(self):
        self.url = "/api/v1/auth/register"
        self.valid_payload = {
            "email": "new@example.com",
            "password": "TestPass1!",
        }

    def test_register_is_disabled(self):
        """A valid payload is refused with 403 and creates no user."""
        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])
        self.assertEqual(User.objects.count(), 0)

    def test_register_disabled_even_with_empty_body(self):
        """The endpoint refuses regardless of payload."""
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(User.objects.count(), 0)
