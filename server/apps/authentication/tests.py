"""
Authentication Tests Module
This module contains tests for the authentication endpoints.
Tests are organized using Django's TestCase class and DRF's APITestCase.
"""

from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.users.models import User
from unittest.mock import patch

from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


class RegistrationTests(APITestCase):
    """
    Test suite for the registration endpoint.
    APITestCase provides useful methods for making API requests and assertions.
    """

    def setUp(self):
        """
        setUp runs before each test method.
        Use it to set up any initial data or state needed for your tests.

        URL Pattern:
        - Base: /api/v1/
        - ViewSet: auth/
        - Action: register/
        - Final URL: /api/v1/auth/register/
        """
        # Define the URL for the registration endpoint using Django's reverse function
        # 'auth-register' comes from the DefaultRouter pattern:
        # {basename}-{url_name} where basename='auth' and url_name='register'
        self.register_url = reverse("auth-register")

        # Define valid test data that we'll use in our tests
        self.valid_payload = {"email": "test@example.com", "password": "TestPass123!"}

    def test_successful_registration(self):
        """
        Test a successful user registration with valid data.
        This test verifies that:
        1. The request returns a 200 OK status
        2. The response contains the expected data structure
        3. A new user is created in the database
        4. A new profile is created for the user
        5. The password is properly hashed (not stored in plain text)
        """
        log.step("Testing successful registration flow")
        # Mock the PowerPath service call to avoid actual API calls during testing
        with patch(
            "apps.profiles.services.PowerPathSyncService.fetch_powerpath_user"
        ) as mock_powerpath:
            # Configure the mock to return None (simulating no existing PowerPath user)
            mock_powerpath.return_value = None
            log.fine("PowerPath service mocked successfully")

            # Make the POST request to the registration endpoint
            log.info("Attempting user registration with valid credentials")
            response = self.client.post(
                self.register_url, self.valid_payload, format="json"
            )

            # Assert that the response status code is 200 OK
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            log.fine("Received 200 OK status")

            # Assert that the response has the expected structure
            self.assertTrue(response.data["success"])
            self.assertIn("user", response.data)
            self.assertIn("profile", response.data)
            self.assertIn("tokens", response.data)
            log.fine("Response structure validation passed")

            # Verify that a user was created in the database
            self.assertTrue(
                User.objects.filter(email=self.valid_payload["email"]).exists()
            )
            log.fine("User exists in database")

            # Get the created user
            user = User.objects.get(email=self.valid_payload["email"])

            # Verify that a profile was created for the user
            self.assertTrue(hasattr(user, "profiles"))
            log.fine("User profile exists")

            # Verify that the password is hashed (not stored as plain text)
            self.assertNotEqual(user.password, self.valid_payload["password"])
            log.fine("Password is properly hashed")

            # Verify that the user can authenticate with the provided password
            self.assertTrue(user.check_password(self.valid_payload["password"]))
            log.fine("Password authentication verified")

            # Log final success after all assertions have passed
            log.success(
                "Successfully completed registration test with all validations passing"
            )

    def test_registration_existing_email(self):
        """
        Test registration attempt with an email that already exists.
        This test verifies that:
        1. The request returns a 400 Bad Request status
        2. The response contains an appropriate error message
        3. No new user is created
        """
        log.step("Testing registration with existing email")
        # First create a user with the test email
        User.objects.create_user(
            email=self.valid_payload["email"], password=self.valid_payload["password"]
        )
        log.info("Created initial user for duplicate email test")

        # Attempt to register with the same email
        log.info("Attempting to register with existing email")
        response = self.client.post(
            self.register_url, self.valid_payload, format="json"
        )

        # Assert that the response status code is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        log.fine("Received 400 Bad Request status")

        # Assert that the response contains an error message
        self.assertFalse(response.data["success"])
        self.assertIn("error", response.data)
        log.fine(f"Error response validation passed: {response.data.get('error', '')}")

        # Verify that no new user was created (count should still be 1)
        self.assertEqual(User.objects.count(), 1)

        # Log final success after all assertions have passed
        log.success(
            "Successfully completed duplicate email test with all validations passing"
        )

    def test_registration_invalid_email(self):
        """
        Test registration attempt with an invalid email format.
        This test verifies that:
        1. The request returns a 400 Bad Request status
        2. The response contains a validation error message
        3. No user is created
        """
        log.step("Testing registration with invalid email format")
        invalid_payload = {
            "email": "invalid-email",  # Invalid email format
            "password": "TestPass123!",
        }
        log.fine(f"Using invalid payload: {invalid_payload}")

        response = self.client.post(self.register_url, invalid_payload, format="json")

        # Assert that the response status code is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        log.fine("Received 400 Bad Request status")

        # Assert that the response contains an error message
        self.assertFalse(response.data["success"])
        self.assertIn("error", response.data)
        log.fine(f"Error response validation passed: {response.data.get('error', '')}")

        # Verify that no user was created
        self.assertEqual(User.objects.count(), 0)

        # Log final success after all assertions have passed
        log.success(
            "Successfully completed invalid email test with all validations passing"
        )

    def test_registration_missing_fields(self):
        """
        Test registration attempt with missing required fields.
        This test verifies that:
        1. The request returns a 400 Bad Request status
        2. The response contains appropriate validation errors
        3. No user is created
        """
        log.step("Testing registration with missing required fields")

        # Test with missing email
        log.info("Testing registration with missing email")
        response_missing_email = self.client.post(
            self.register_url, {"password": "TestPass123!"}, format="json"
        )
        self.assertEqual(
            response_missing_email.status_code, status.HTTP_400_BAD_REQUEST
        )
        log.fine("Missing email validation passed")

        # Test with missing password
        log.info("Testing registration with missing password")
        response_missing_password = self.client.post(
            self.register_url, {"email": "test@example.com"}, format="json"
        )
        self.assertEqual(
            response_missing_password.status_code, status.HTTP_400_BAD_REQUEST
        )
        log.fine("Missing password validation passed")

        # Verify that no user was created
        self.assertEqual(User.objects.count(), 0)

        # Log final success after all assertions have passed
        log.success(
            "Successfully completed missing fields test with all validations passing"
        )
