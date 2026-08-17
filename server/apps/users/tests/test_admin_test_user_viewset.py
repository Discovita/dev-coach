"""
Endpoint tests for `AdminTestUserViewSet`.

Covers the admin parity of derived user-state fields — in particular
that `on_break` is exposed on `/api/v1/admin/test-user/{pk}/coach-state`
so admin impersonation sees the same shape as the regular user-state
endpoints — plus the super-admin-only Studio access override and user
deletion endpoints.
"""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.chat_messages.models import ChatMessage
from apps.coach_states.models import Break, CoachState
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


class AdminTestUserStudioAccessTests(APITestCase):
    """Super-admin-only tri-state Studio access override endpoint."""

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            email="super@example.com",
            password="superpass123",
        )
        self.staff = User.objects.create_user(
            email="staff@example.com",
            password="staffpass123",
            is_staff=True,
        )
        self.target_user = User.objects.create_user(
            email="target@example.com",
            password="testpass123",
        )

    def _url(self, user: User) -> str:
        return f"/api/v1/admin/test-user/{user.pk}/studio-access"

    def test_superuser_can_force_unlock(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.patch(
            self._url(self.target_user),
            {"studio_access_override": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["studio_access_override"])
        self.target_user.coach_state.refresh_from_db()
        self.assertTrue(self.target_user.coach_state.studio_access_override)

    def test_superuser_can_force_lock(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.patch(
            self._url(self.target_user),
            {"studio_access_override": False},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["studio_access_override"])
        self.target_user.coach_state.refresh_from_db()
        self.assertFalse(self.target_user.coach_state.studio_access_override)

    def test_superuser_can_reset_to_default(self):
        self.target_user.coach_state.studio_access_override = True
        self.target_user.coach_state.save(update_fields=["studio_access_override"])
        self.client.force_authenticate(user=self.superuser)
        response = self.client.patch(
            self._url(self.target_user),
            {"studio_access_override": None},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["studio_access_override"])
        self.target_user.coach_state.refresh_from_db()
        self.assertIsNone(self.target_user.coach_state.studio_access_override)

    def test_missing_field_is_rejected(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.patch(self._url(self.target_user), {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_value_is_rejected(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.patch(
            self._url(self.target_user),
            {"studio_access_override": "maybe"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_staff_admin_is_forbidden(self):
        """is_staff alone is not enough — this is a super-admin capability."""
        self.client.force_authenticate(user=self.staff)
        response = self.client.patch(
            self._url(self.target_user),
            {"studio_access_override": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_is_forbidden(self):
        response = self.client.patch(
            self._url(self.target_user),
            {"studio_access_override": True},
            format="json",
        )
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )


class AdminTestUserDeleteTests(APITestCase):
    """Super-admin-only permanent user deletion."""

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            email="super@example.com",
            password="superpass123",
        )
        self.staff = User.objects.create_user(
            email="staff@example.com",
            password="staffpass123",
            is_staff=True,
        )
        self.target_user = User.objects.create_user(
            email="target@example.com",
            password="testpass123",
        )

    def _url(self, user: User) -> str:
        return f"/api/v1/admin/test-user/{user.pk}/delete"

    def test_superuser_can_delete_a_user(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.delete(self._url(self.target_user))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=self.target_user.pk).exists())

    def test_delete_cascades_to_the_users_data(self):
        """Rows hanging off the user go with them; other users are untouched."""
        ChatMessage.objects.create(
            user=self.target_user,
            role="user",
            content="Hello",
        )
        Break.objects.create(
            user=self.target_user,
            triggered_by_session="get_to_know_session",
        )
        survivor = User.objects.create_user(
            email="survivor@example.com",
            password="testpass123",
        )
        ChatMessage.objects.create(user=survivor, role="user", content="Still here")

        self.client.force_authenticate(user=self.superuser)
        response = self.client.delete(self._url(self.target_user))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            ChatMessage.objects.filter(user_id=self.target_user.pk).exists()
        )
        self.assertFalse(Break.objects.filter(user_id=self.target_user.pk).exists())
        self.assertFalse(
            CoachState.objects.filter(user_id=self.target_user.pk).exists()
        )
        self.assertTrue(User.objects.filter(pk=survivor.pk).exists())
        self.assertEqual(ChatMessage.objects.filter(user=survivor).count(), 1)

    def test_superuser_cannot_delete_themselves(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.delete(self._url(self.superuser))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(User.objects.filter(pk=self.superuser.pk).exists())

    def test_staff_admin_is_forbidden(self):
        """is_staff alone is not enough — this is a super-admin capability."""
        self.client.force_authenticate(user=self.staff)
        response = self.client.delete(self._url(self.target_user))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(User.objects.filter(pk=self.target_user.pk).exists())

    def test_anonymous_is_forbidden(self):
        response = self.client.delete(self._url(self.target_user))

        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )
        self.assertTrue(User.objects.filter(pk=self.target_user.pk).exists())

    def test_unknown_user_returns_404(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.delete(
            "/api/v1/admin/test-user/00000000-0000-0000-0000-000000000000/delete"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
