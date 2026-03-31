"""
Endpoint tests for POST /api/v1/auth/login/.
"""

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from apps.authentication.serializers import LoginSerializer
from apps.users.models import User


class LoginSerializerTests(TestCase):
    """Tests for LoginSerializer validation."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="login@example.com", password="TestPass1!"
        )

    def test_valid_credentials_pass(self):
        """Correct email/password should validate and attach user."""
        serializer = LoginSerializer(
            data={"email": "login@example.com", "password": "TestPass1!"}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["user"], self.user)

    def test_wrong_password_rejected(self):
        """Wrong password should fail validation."""
        serializer = LoginSerializer(
            data={"email": "login@example.com", "password": "WrongPass1!"}
        )
        self.assertFalse(serializer.is_valid())

    def test_nonexistent_email_rejected(self):
        """Unknown email should fail validation."""
        serializer = LoginSerializer(
            data={"email": "nobody@example.com", "password": "TestPass1!"}
        )
        self.assertFalse(serializer.is_valid())

    def test_missing_email_rejected(self):
        """Missing email field should fail."""
        serializer = LoginSerializer(data={"password": "TestPass1!"})
        self.assertFalse(serializer.is_valid())

    def test_missing_password_rejected(self):
        """Missing password field should fail."""
        serializer = LoginSerializer(data={"email": "login@example.com"})
        self.assertFalse(serializer.is_valid())


class LoginEndpointTests(APITestCase):
    """Tests for the POST /api/v1/auth/login/ endpoint."""

    def setUp(self):
        self.url = "/api/v1/auth/login"
        self.user = User.objects.create_user(
            email="login@example.com", password="TestPass1!"
        )

    def test_successful_login(self):
        """Valid credentials return tokens."""
        response = self.client.post(
            self.url,
            {"email": "login@example.com", "password": "TestPass1!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("tokens", response.data)
        self.assertEqual(response.data["user_id"], self.user.id)

    def test_wrong_password_returns_400(self):
        """Invalid password returns 400."""
        response = self.client.post(
            self.url,
            {"email": "login@example.com", "password": "Wrong1!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_nonexistent_user_returns_400(self):
        """Unknown email returns 400."""
        response = self.client.post(
            self.url,
            {"email": "nobody@example.com", "password": "TestPass1!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_fields_returns_400(self):
        """Empty body returns 400."""
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
