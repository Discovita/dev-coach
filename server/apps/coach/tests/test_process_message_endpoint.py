"""
Endpoint tests for POST /api/v1/coach/process-message/
"""

from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User


PROCESS_MESSAGE_PATH = "apps.coach.views.coach_view_set.process_message"
URL = "/api/v1/coach/process-message"

VALID_RESPONSE_DATA = {
    "message": "Hello from coach",
    "final_prompt": "You are a life coach.",
    "on_break": False,
}


class TestProcessMessageEndpoint(APITestCase):
    """Tests for the POST /api/v1/coach/process-message/ endpoint."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com", password="Pass1!"
        )
        self.client.force_authenticate(user=self.user)

    def test_unauthenticated_request_returns_401(self):
        """Unauthenticated callers are rejected."""
        self.client.logout()
        response = self.client.post(URL, {"message": "Hello"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_message_and_actions_returns_400(self):
        """Empty request body returns 400."""
        response = self.client.post(URL, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch(PROCESS_MESSAGE_PATH)
    def test_successful_response_returns_200(self, mock_process):
        """Valid request with successful processing returns 200."""
        mock_process.return_value = (True, VALID_RESPONSE_DATA, None)

        response = self.client.post(URL, {"message": "Hello"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Hello from coach")
        self.assertEqual(response.data["final_prompt"], "You are a life coach.")

    @patch(PROCESS_MESSAGE_PATH)
    def test_process_message_failure_returns_500(self, mock_process):
        """When process_message returns failure, the endpoint returns 500."""
        mock_process.return_value = (False, {}, "AI service unavailable")

        response = self.client.post(URL, {"message": "Hello"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("detail", response.data)

    @patch(PROCESS_MESSAGE_PATH)
    def test_calls_process_message_with_correct_user(self, mock_process):
        """The authenticated user is passed to process_message."""
        mock_process.return_value = (True, VALID_RESPONSE_DATA, None)

        self.client.post(URL, {"message": "Hi"}, format="json")

        call_kwargs = mock_process.call_args.kwargs
        self.assertEqual(call_kwargs["user"], self.user)

    @patch(PROCESS_MESSAGE_PATH)
    def test_calls_process_message_with_correct_message(self, mock_process):
        """The message field is forwarded to process_message."""
        mock_process.return_value = (True, VALID_RESPONSE_DATA, None)

        self.client.post(URL, {"message": "Test message"}, format="json")

        call_kwargs = mock_process.call_args.kwargs
        self.assertEqual(call_kwargs["message"], "Test message")

    @patch(PROCESS_MESSAGE_PATH)
    def test_component_included_when_present(self, mock_process):
        """A 'component' key in the response data is forwarded to the client."""
        response_with_component = {
            **VALID_RESPONSE_DATA,
            "component": {"type": "accept_identity", "data": {}},
        }
        mock_process.return_value = (True, response_with_component, None)

        response = self.client.post(URL, {"message": "Hi"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("component", response.data)
        self.assertEqual(response.data["component"]["type"], "accept_identity")
