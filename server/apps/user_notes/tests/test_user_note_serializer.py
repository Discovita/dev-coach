"""
Tests for the UserNoteSerializer.
"""

from django.test import TestCase

from apps.chat_messages.models import ChatMessage
from apps.user_notes.models import UserNote
from apps.user_notes.serializers import UserNoteSerializer
from apps.users.models import User


class TestUserNoteSerializer(TestCase):
    """Tests for UserNoteSerializer field enumeration and read-only behaviour."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="serializeruser@test.com",
            password="TestPass123!",
            first_name="Ser",
            last_name="Ializer",
        )
        cls.message = ChatMessage.objects.create(
            user=cls.user,
            role="user",
            content="Some message.",
        )
        cls.note = UserNote.objects.create(
            user=cls.user,
            note="Likes Python.",
            source_message=cls.message,
        )

    def test_serialized_fields(self):
        data = UserNoteSerializer(self.note).data
        expected_keys = {
            "id",
            "user",
            "note",
            "source_message",
            "created_at",
            "test_scenario",
        }
        self.assertEqual(set(data.keys()), expected_keys)

    def test_id_is_read_only(self):
        """Providing an id in input should be ignored."""
        import uuid

        custom_id = str(uuid.uuid4())
        serializer = UserNoteSerializer(
            data={
                "id": custom_id,
                "user": str(self.user.id),
                "note": "New note.",
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertNotEqual(str(instance.id), custom_id)

    def test_created_at_is_read_only(self):
        """Providing created_at in input should be ignored."""
        serializer = UserNoteSerializer(
            data={
                "user": str(self.user.id),
                "note": "Another note.",
                "created_at": "2000-01-01T00:00:00Z",
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertNotEqual(instance.created_at.year, 2000)

    def test_valid_minimal_input(self):
        serializer = UserNoteSerializer(
            data={"user": str(self.user.id), "note": "Minimal note."}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_missing_required_note_field(self):
        serializer = UserNoteSerializer(data={"user": str(self.user.id)})
        self.assertFalse(serializer.is_valid())
        self.assertIn("note", serializer.errors)

    def test_missing_required_user_field(self):
        serializer = UserNoteSerializer(data={"note": "Orphan note."})
        self.assertFalse(serializer.is_valid())
        self.assertIn("user", serializer.errors)
