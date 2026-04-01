"""
Tests for gather_user_notes_section function.
"""

from django.test import TestCase

from apps.test_scenario.utils import gather_user_notes_section
from apps.user_notes.models import UserNote
from apps.users.models import User


class TestGatherUserNotesSection(TestCase):
    """gather_user_notes_section tests."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="gather_un@example.com", password="testpass"
        )

    # ==================== Empty case ====================

    def test_returns_empty_list_when_no_notes(self):
        """Should return an empty list when the user has no notes."""
        result = gather_user_notes_section(self.user)
        self.assertEqual(result, [])

    # ==================== Basic output ====================

    def test_section_contains_note_field(self):
        """Each entry should have a 'note' key."""
        UserNote.objects.create(user=self.user, note="Remember this.")
        result = gather_user_notes_section(self.user)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["note"], "Remember this.")

    def test_created_at_included_as_iso_string(self):
        """Should include created_at as ISO string when present."""
        from django.utils import timezone
        note = UserNote.objects.create(
            user=self.user, note="Note", created_at=timezone.now()
        )
        result = gather_user_notes_section(self.user)
        self.assertIn("created_at", result[0])
        self.assertIsInstance(result[0]["created_at"], str)

    def test_multiple_notes_all_returned(self):
        """Should return all notes for the user."""
        UserNote.objects.create(user=self.user, note="Note 1")
        UserNote.objects.create(user=self.user, note="Note 2")
        result = gather_user_notes_section(self.user)
        self.assertEqual(len(result), 2)

    def test_does_not_return_other_users_notes(self):
        """Should only return notes for the specified user."""
        other = User.objects.create_user(
            email="other_gather_un@example.com", password="testpass"
        )
        UserNote.objects.create(user=other, note="Not mine")
        result = gather_user_notes_section(self.user)
        self.assertEqual(result, [])
