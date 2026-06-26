"""
Tests for the invite-only access flow.

Covers:
- Invite model helpers (expiry / accepted / pending).
- Super-admin invite management endpoints (create / list / resend / revoke),
  including the IsSuperUser gate.
- Public invite validation + register-via-invite (account creation, login,
  single-use, expiry).
"""

from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.authentication.models import Invite
from apps.users.models import User

# Where send_invite_email is referenced (admin viewset) — patch the seam there.
SEND_INVITE = "apps.authentication.views.admin_invite_viewset.send_invite_email"


class InviteModelTests(APITestCase):
    """Invite model derived-state helpers."""

    def test_new_invite_is_pending(self):
        invite = Invite.objects.create(email="a@example.com")
        self.assertTrue(invite.is_pending)
        self.assertFalse(invite.is_accepted)
        self.assertFalse(invite.is_expired)
        self.assertEqual(len(invite.token), 64)

    def test_expired_invite(self):
        invite = Invite.objects.create(
            email="a@example.com",
            expires_at=timezone.now() - timedelta(days=1),
        )
        self.assertTrue(invite.is_expired)
        self.assertFalse(invite.is_pending)

    def test_accepted_invite(self):
        invite = Invite.objects.create(email="a@example.com")
        invite.mark_accepted()
        invite.save()
        self.assertTrue(invite.is_accepted)
        self.assertFalse(invite.is_pending)


@patch(SEND_INVITE, return_value=True)
class AdminInviteEndpointTests(APITestCase):
    """Super-admin-only invite management."""

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            email="super@example.com", password="superpass123"
        )
        self.staff = User.objects.create_user(
            email="staff@example.com", password="staffpass123", is_staff=True
        )
        self.url = "/api/v1/admin/invites"

    def test_superuser_can_create_invite(self, mock_send):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(
            self.url, {"email": "invitee@example.com"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "invitee@example.com")
        self.assertEqual(response.data["status"], "pending")
        self.assertTrue(response.data["email_sent"])
        invite = Invite.objects.get(email="invitee@example.com")
        self.assertEqual(invite.invited_by, self.superuser)
        mock_send.assert_called_once()

    def test_staff_cannot_create_invite(self, mock_send):
        self.client.force_authenticate(user=self.staff)
        response = self.client.post(
            self.url, {"email": "invitee@example.com"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_list_invites(self, mock_send):
        response = self.client.get(self.url)
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_create_rejects_existing_user_email(self, mock_send):
        User.objects.create_user(email="taken@example.com", password="pass123")
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(
            self.url, {"email": "taken@example.com"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_reuses_pending_invite(self, mock_send):
        self.client.force_authenticate(user=self.superuser)
        self.client.post(self.url, {"email": "dup@example.com"}, format="json")
        self.client.post(self.url, {"email": "dup@example.com"}, format="json")
        self.assertEqual(Invite.objects.filter(email="dup@example.com").count(), 1)

    def test_resend_refreshes_expiry(self, mock_send):
        invite = Invite.objects.create(
            email="r@example.com",
            expires_at=timezone.now() + timedelta(days=1),
        )
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(f"{self.url}/{invite.id}/resend")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invite.refresh_from_db()
        self.assertGreater(invite.expires_at, timezone.now() + timedelta(days=6))

    def test_revoke_deletes_invite(self, mock_send):
        invite = Invite.objects.create(email="x@example.com")
        self.client.force_authenticate(user=self.superuser)
        response = self.client.delete(f"{self.url}/{invite.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Invite.objects.filter(id=invite.id).exists())


class PublicInviteFlowTests(APITestCase):
    """Public invite validation + register-via-invite."""

    def setUp(self):
        self.invite = Invite.objects.create(email="new@example.com")
        self.validate_url = f"/api/v1/auth/invites/{self.invite.token}"
        self.register_url = "/api/v1/auth/register-via-invite"

    def test_validate_returns_locked_email(self):
        response = self.client.get(self.validate_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "new@example.com")

    def test_validate_invalid_token(self):
        response = self.client.get("/api/v1/auth/invites/deadbeef")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validate_expired_token(self):
        self.invite.expires_at = timezone.now() - timedelta(days=1)
        self.invite.save()
        response = self.client.get(self.validate_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_via_invite_creates_verified_logged_in_user(self):
        response = self.client.post(
            self.register_url,
            {"token": self.invite.token, "password": "GoodPass1!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("tokens", response.data)
        user = User.objects.get(email="new@example.com")
        self.assertTrue(user.is_email_verified)
        self.invite.refresh_from_db()
        self.assertTrue(self.invite.is_accepted)

    def test_register_via_invite_is_single_use(self):
        self.client.post(
            self.register_url,
            {"token": self.invite.token, "password": "GoodPass1!"},
            format="json",
        )
        response = self.client.post(
            self.register_url,
            {"token": self.invite.token, "password": "GoodPass1!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.filter(email="new@example.com").count(), 1)

    def test_register_via_invite_weak_password_rejected(self):
        response = self.client.post(
            self.register_url,
            {"token": self.invite.token, "password": "weak"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_register_via_invite_expired_rejected(self):
        self.invite.expires_at = timezone.now() - timedelta(days=1)
        self.invite.save()
        response = self.client.post(
            self.register_url,
            {"token": self.invite.token, "password": "GoodPass1!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
