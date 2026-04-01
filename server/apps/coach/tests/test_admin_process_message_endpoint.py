"""
Endpoint tests for POST /api/v1/admin/coach/process-message-for-user/
"""

from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User


PROCESS_MESSAGE_PATH = "apps.coach.views.admin_coach_view_set.process_message"
URL = "/api/v1/admin/coach/process-message-for-user"

VALID_RESPONSE_DATA = {
    "message": "Hello from coach",
    "final_prompt": "You are a life coach.",
}


def _make_admin(**kwargs):
    defaults = {"email": "admin@example.com", "password": "AdminPass1!"}
    defaults.update(kwargs)
    user = User.objects.create_user(**defaults)
    user.is_staff = True
    user.save()
    return user


def _make_user(**kwargs):
    defaults = {"email": "target@example.com", "password": "Pass1!"}
    defaults.update(kwargs)
    return User.objects.create_user(**defaults)


class TestAdminProcessMessageEndpoint(APITestCase):
    """Tests for POST /api/v1/admin/coach/process-message-for-user/."""

    def setUp(self):
        self.admin = _make_admin()
        self.target_user = _make_user()
        self.client.force_authenticate(user=self.admin)

    def _payload(self, **overrides):
        base = {"user_id": str(self.target_user.id), "message": "Hello"}
        base.update(overrides)
        return base

    def test_unauthenticated_request_returns_401(self):
        """Unauthenticated callers are rejected before permission checks."""
        self.client.logout()
        response = self.client.post(URL, self._payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_admin_user_returns_403(self):
        """Non-staff, non-superuser callers are denied."""
        regular_user = _make_user(email="regular@example.com")
        self.client.force_authenticate(user=regular_user)

        response = self.client.post(URL, self._payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_missing_user_id_returns_400(self):
        """Request without user_id is invalid."""
        response = self.client.post(URL, {"message": "Hi"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nonexistent_user_id_returns_404(self):
        """A valid UUID that doesn't match any user returns 404."""
        payload = self._payload(user_id="00000000-0000-0000-0000-000000000000")
        response = self.client.post(URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch(PROCESS_MESSAGE_PATH)
    def test_successful_response_returns_200(self, mock_process):
        """Valid admin request with successful processing returns 200."""
        mock_process.return_value = (True, VALID_RESPONSE_DATA, None)

        response = self.client.post(URL, self._payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Hello from coach")

    @patch(PROCESS_MESSAGE_PATH)
    def test_process_message_failure_returns_500(self, mock_process):
        """When process_message fails, the endpoint returns 500."""
        mock_process.return_value = (False, {}, "AI error")

        response = self.client.post(URL, self._payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("detail", response.data)

    @patch(PROCESS_MESSAGE_PATH)
    def test_calls_process_message_with_target_user(self, mock_process):
        """process_message receives the target user, not the admin."""
        mock_process.return_value = (True, VALID_RESPONSE_DATA, None)

        self.client.post(URL, self._payload(), format="json")

        call_kwargs = mock_process.call_args.kwargs
        self.assertEqual(call_kwargs["user"].id, self.target_user.id)

    @patch(PROCESS_MESSAGE_PATH)
    def test_superuser_is_also_permitted(self, mock_process):
        """A superuser (not is_staff) can access the admin endpoint."""
        mock_process.return_value = (True, VALID_RESPONSE_DATA, None)
        superuser = _make_user(email="super@example.com")
        superuser.is_superuser = True
        superuser.save()
        self.client.force_authenticate(user=superuser)

        response = self.client.post(URL, self._payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
