"""
Tests for IdentityImageChat model.
"""

from django.test import TestCase
from django.db import IntegrityError

from apps.identities.models import Identity, IdentityImageChat
from apps.users.models import User
from enums.identity_category import IdentityCategory


class IdentityImageChatModelTests(TestCase):
    """Tests for IdentityImageChat model methods and properties."""

    def setUp(self):
        """Create test user and identity."""
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        self.identity = Identity.objects.create(
            user=self.user,
            name="The Artist",
            category=IdentityCategory.PASSIONS,
        )

    def test_create_chat_record(self):
        """Test that we can create a chat record for a user."""
        chat = IdentityImageChat.objects.create(
            user=self.user,
            identity=self.identity,
            chat_history=[],
        )
        
        self.assertIsNotNone(chat.id)
        self.assertEqual(chat.user, self.user)
        self.assertEqual(chat.identity, self.identity)
        self.assertEqual(chat.chat_history, [])

    def test_one_to_one_constraint(self):
        """Test that only one chat per user is allowed (update_or_create works)."""
        # Create first chat
        chat1, created1 = IdentityImageChat.objects.update_or_create(
            user=self.user,
            defaults={
                "identity": self.identity,
                "chat_history": [{"role": "user", "parts": ["test"]}],
            },
        )
        self.assertTrue(created1)
        
        # Try to create another chat for same user - should update existing
        chat2, created2 = IdentityImageChat.objects.update_or_create(
            user=self.user,
            defaults={
                "identity": self.identity,
                "chat_history": [{"role": "user", "parts": ["updated"]}],
            },
        )
        self.assertFalse(created2)
        self.assertEqual(chat1.id, chat2.id)
        self.assertEqual(chat2.chat_history, [{"role": "user", "parts": ["updated"]}])

    def test_identity_nullable(self):
        """Test that identity FK can be null."""
        chat = IdentityImageChat.objects.create(
            user=self.user,
            identity=None,
            chat_history=[],
        )
        
        self.assertIsNone(chat.identity)

    def test_cascade_delete_with_user(self):
        """Test that chat is deleted when user is deleted."""
        chat = IdentityImageChat.objects.create(
            user=self.user,
            identity=self.identity,
            chat_history=[],
        )
        chat_id = chat.id
        
        # Delete user
        self.user.delete()
        
        # Chat should be deleted
        self.assertFalse(IdentityImageChat.objects.filter(id=chat_id).exists())

    def test_chat_history_default_empty(self):
        """Test that chat_history defaults to empty list."""
        chat = IdentityImageChat.objects.create(
            user=self.user,
            identity=self.identity,
        )
        
        self.assertEqual(chat.chat_history, [])

    def test_str_representation(self):
        """Test __str__ returns expected format."""
        chat = IdentityImageChat.objects.create(
            user=self.user,
            identity=self.identity,
            chat_history=[],
        )
        
        expected = f"ImageChat for {self.user.email} - {self.identity.name}"
        self.assertEqual(str(chat), expected)

    def test_str_representation_no_identity(self):
        """Test __str__ when identity is None."""
        chat = IdentityImageChat.objects.create(
            user=self.user,
            identity=None,
            chat_history=[],
        )
        
        expected = f"ImageChat for {self.user.email} - No identity"
        self.assertEqual(str(chat), expected)

    def test_chat_history_stores_json(self):
        """Test that chat_history can store complex JSON data."""
        complex_history = [
            {
                "role": "user",
                "parts": [{"text": "Generate an image"}]
            },
            {
                "role": "model",
                "parts": [
                    {"text": "I'll generate that for you"},
                    {"inline_data": {"mime_type": "image/png", "data": "base64data"}}
                ]
            }
        ]
        
        chat = IdentityImageChat.objects.create(
            user=self.user,
            identity=self.identity,
            chat_history=complex_history,
        )
        
        # Refresh from database
        chat.refresh_from_db()
        self.assertEqual(chat.chat_history, complex_history)

    def test_identity_set_null_on_delete(self):
        """Test that identity FK is set to NULL when identity is deleted."""
        chat = IdentityImageChat.objects.create(
            user=self.user,
            identity=self.identity,
            chat_history=[],
        )
        
        # Delete identity
        self.identity.delete()
        
        # Refresh chat from database
        chat.refresh_from_db()
        self.assertIsNone(chat.identity)
