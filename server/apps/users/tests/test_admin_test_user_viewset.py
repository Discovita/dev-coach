"""
Endpoint tests for `AdminTestUserViewSet`.

Covers the admin parity of derived user-state fields — in particular
that `on_break` is exposed on `/api/v1/admin/test-user/{pk}/coach-state`
so admin impersonation sees the same shape as the regular user-state
endpoints.
"""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.coach_states.models import Break
from apps.users.models import User


class AdminTestUserViewSetOnBreakTests(APITestCase):
    """`on_break` parity for the admin test-user endpoints."""

    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass123",
        )
        self.target_user = User.objects.create_user(
            email="target@example.com",
            password="testpass123",
        )
        # Signal auto-creates a CoachState for both users.
        self.client.force_authenticate(user=self.admin)

    def _coach_state_url(self, user: User) -> str:
        return f"/api/v1/admin/test-user/{user.pk}/coach-state"

    def test_admin_test_user_state_includes_on_break_field(self):
        """The admin coach-state response carries `on_break` (False with no break)."""
        response = self.client.get(self._coach_state_url(self.target_user))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("on_break", response.data)
        self.assertFalse(response.data["on_break"])

    def test_admin_test_user_state_on_break_true_when_open_break(self):
        """An open Break for the target user surfaces `on_break: True` over the admin endpoint."""
        Break.objects.create(
            user=self.target_user,
            triggered_by_session="get_to_know_session",
        )

        response = self.client.get(self._coach_state_url(self.target_user))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["on_break"])
