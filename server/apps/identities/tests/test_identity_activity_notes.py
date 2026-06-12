"""
Tests that identity edits/deletes made through the app record a UserNote (so
the coaching agent is aware of out-of-session changes), plus the admin
delete-identity endpoint used during impersonation.
"""

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.identities.models import Identity
from apps.user_notes.models import UserNote
from apps.users.models import User
from enums.identity_category import IdentityCategory


def _make_identity(user, name, **kwargs):
    return Identity.objects.create(
        user=user, name=name, category=IdentityCategory.PASSIONS, **kwargs
    )


class UserIdentityActivityNoteTests(APITestCase):
    """The user-facing edit (PATCH) and delete (DELETE) endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="notes@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.identity = _make_identity(self.user, "Acrobat")

    def test_rename_records_a_note(self):
        response = self.client.patch(
            f"/api/v1/identities/{self.identity.id}",
            {"name": "Fitness Enthusiast"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        notes = UserNote.objects.filter(user=self.user)
        self.assertEqual(notes.count(), 1)
        self.assertIn("Acrobat", notes.first().note)
        self.assertIn("Fitness Enthusiast", notes.first().note)

    def test_i_am_statement_edit_records_a_note(self):
        response = self.client.patch(
            f"/api/v1/identities/{self.identity.id}",
            {"i_am_statement": "I am unstoppable."},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UserNote.objects.filter(user=self.user).count(), 1)
        self.assertIn("I am unstoppable.", UserNote.objects.first().note)

    def test_scene_only_edit_records_no_note(self):
        response = self.client.patch(
            f"/api/v1/identities/{self.identity.id}",
            {"clothing": "linen shirt", "mood": "calm"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UserNote.objects.filter(user=self.user).count(), 0)

    def test_delete_records_a_note_and_removes_identity(self):
        response = self.client.delete(f"/api/v1/identities/{self.identity.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Identity.objects.filter(id=self.identity.id).exists())
        notes = UserNote.objects.filter(user=self.user)
        self.assertEqual(notes.count(), 1)
        self.assertIn("deleted", notes.first().note.lower())
        self.assertIn("Acrobat", notes.first().note)


class AdminIdentityDeleteTests(APITestCase):
    """The admin delete-identity endpoint (impersonation)."""

    URL = "/api/v1/admin/identities/delete-identity"

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email="admin@example.com", password="testpass123", is_staff=True
        )
        self.target = User.objects.create_user(
            email="target@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.admin)
        self.identity = _make_identity(self.target, "Acrobat")

    def test_admin_deletes_target_identity_and_records_note(self):
        response = self.client.delete(f"{self.URL}?identity_id={self.identity.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Identity.objects.filter(id=self.identity.id).exists())
        # Note is recorded against the target user, not the admin.
        self.assertEqual(UserNote.objects.filter(user=self.target).count(), 1)
        self.assertEqual(UserNote.objects.filter(user=self.admin).count(), 0)

    def test_admin_edit_records_note_for_target_user(self):
        response = self.client.patch(
            "/api/v1/admin/identities/update-identity",
            {"identity_id": str(self.identity.id), "name": "Marathoner"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notes = UserNote.objects.filter(user=self.target)
        self.assertEqual(notes.count(), 1)
        self.assertIn("Marathoner", notes.first().note)

    def test_missing_identity_id_is_rejected(self):
        response = self.client.delete(self.URL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_admin_is_forbidden(self):
        self.client.force_authenticate(user=self.target)
        response = self.client.delete(f"{self.URL}?identity_id={self.identity.id}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Identity.objects.filter(id=self.identity.id).exists())
