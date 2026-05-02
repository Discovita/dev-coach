"""
Tests for the UserNote model.
"""

import uuid

from django.test import TestCase

from apps.chat_messages.models import ChatMessage
from apps.user_notes.models import UserNote
from apps.users.models import User


class TestUserNoteModel(TestCase):
    """Tests for UserNote model fields, defaults, and relationships."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="noteuser@test.com",
            password="TestPass123!",
            first_name="Note",
            last_name="User",
        )
        cls.message = ChatMessage.objects.create(
            user=cls.user,
            role="user",
            content="I love hiking in the mountains.",
        )

    def test_create_minimal_note(self):
        note = UserNote.objects.create(user=self.user, note="Enjoys hiking.")
        self.assertIsNotNone(note.id)
        self.assertIsInstance(note.id, uuid.UUID)
        self.assertEqual(note.note, "Enjoys hiking.")
        self.assertIsNone(note.source_message)
        self.assertIsNone(note.test_scenario)
        self.assertIsNotNone(note.created_at)

    def test_create_note_with_source_message(self):
        note = UserNote.objects.create(
            user=self.user,
            note="Loves outdoor activities.",
            source_message=self.message,
        )
        self.assertEqual(note.source_message, self.message)

    def test_uuid_is_unique(self):
        note1 = UserNote.objects.create(user=self.user, note="Note 1")
        note2 = UserNote.objects.create(user=self.user, note="Note 2")
        self.assertNotEqual(note1.id, note2.id)

    def test_str_representation(self):
        note = UserNote.objects.create(
            user=self.user,
            note="This is a very long note that should be truncated in the string representation.",
        )
        result = str(note)
        self.assertIn("noteuser@test.com", result)
        self.assertTrue(result.endswith("..."))
        self.assertLessEqual(len(result.split(": ", 1)[1]), 44)

    def test_cascade_delete_user(self):
        """Deleting the user should cascade-delete all their notes."""
        user = User.objects.create_user(email="ephemeral@test.com", password="Pass123!")
        UserNote.objects.create(user=user, note="Will be deleted.")
        user_id = user.id
        self.assertEqual(UserNote.objects.filter(user_id=user_id).count(), 1)
        user.delete()
        self.assertEqual(UserNote.objects.filter(user_id=user_id).count(), 0)

    def test_source_message_set_null_on_delete(self):
        """Deleting the source message should set the FK to NULL, not delete the note."""
        msg = ChatMessage.objects.create(
            user=self.user, role="user", content="Temporary message."
        )
        note = UserNote.objects.create(
            user=self.user, note="Linked note.", source_message=msg
        )
        msg.delete()
        note.refresh_from_db()
        self.assertIsNone(note.source_message)

    def test_related_name_user_notes(self):
        UserNote.objects.create(user=self.user, note="Note A")
        UserNote.objects.create(user=self.user, note="Note B")
        self.assertEqual(self.user.user_notes.count(), 2)
