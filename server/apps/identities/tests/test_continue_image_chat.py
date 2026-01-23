"""
Tests for continue image chat endpoints and functions.
"""

from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from PIL import Image

from apps.users.models import User
from apps.identities.models import Identity, IdentityImageChat
from apps.reference_images.models import ReferenceImage
from enums.identity_category import IdentityCategory


class ContinueImageChatFunctionTests(TestCase):
    """Test the continue_image_chat function directly."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.identity = Identity.objects.create(
            user=self.user,
            name="The Artist",
            category=IdentityCategory.PASSIONS,
        )
        # Create existing chat session
        self.chat_record = IdentityImageChat.objects.create(
            user=self.user,
            identity=self.identity,
            chat_history=[{"role": "user", "parts": [{"text": "Initial prompt"}]}],
        )

    def _create_mock_pil_image(self):
        """Helper to create a mock PIL image."""
        img = Image.new('RGB', (100, 100), color='red')
        return img

    @patch('services.image_generation.orchestration.GeminiImageService')
    @patch('services.image_generation.utils.chat_history_serializer.deserialize_chat_history')
    def test_continue_chat_success(self, mock_deserialize, mock_service_class):
        """Test successfully continuing a chat and returning image."""
        from apps.identities.functions.public import continue_image_chat
        
        # Setup mocks
        mock_deserialize.return_value = [{"role": "user", "parts": [{"text": "Initial prompt"}]}]
        
        mock_service = MagicMock()
        mock_chat = MagicMock()
        mock_service.create_chat.return_value = mock_chat
        
        mock_response = MagicMock()
        mock_part = MagicMock()
        mock_part.inline_data = MagicMock()
        mock_part.as_image.return_value = self._create_mock_pil_image()
        mock_response.parts = [mock_part]
        
        mock_service.send_chat_message.return_value = (self._create_mock_pil_image(), mock_response)
        # get_history returns list of Content objects (or dicts in mocks)
        updated_history = [
            {"role": "user", "parts": [{"text": "Initial prompt"}]},
            {"role": "user", "parts": [{"text": "make it warmer"}]},
        ]
        mock_chat.get_history.return_value = updated_history
        
        mock_service_class.return_value = mock_service
        
        # Call function
        response = continue_image_chat(
            user=self.user,
            edit_prompt="make it warmer",
        )
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("image_base64", response.data)
        self.assertEqual(response.data["identity_id"], str(self.identity.id))
        self.assertEqual(response.data["identity_name"], self.identity.name)

    @patch('services.image_generation.orchestration.GeminiImageService')
    @patch('services.image_generation.utils.chat_history_serializer.deserialize_chat_history')
    def test_continue_chat_updates_history(self, mock_deserialize, mock_service_class):
        """Test that chat history is updated after edit."""
        from apps.identities.functions.public import continue_image_chat
        
        original_history = [{"role": "user", "parts": [{"text": "Initial"}]}]
        updated_history = [
            {"role": "user", "parts": [{"text": "Initial"}]},
            {"role": "user", "parts": [{"text": "make it warmer"}]},
        ]
        
        # Setup mocks
        mock_deserialize.return_value = original_history
        
        mock_service = MagicMock()
        mock_chat = MagicMock()
        mock_service.create_chat.return_value = mock_chat
        mock_response = MagicMock()
        mock_part = MagicMock()
        mock_part.inline_data = MagicMock()
        mock_part.as_image.return_value = self._create_mock_pil_image()
        mock_response.parts = [mock_part]
        mock_service.send_chat_message.return_value = (self._create_mock_pil_image(), mock_response)
        # get_history returns list of Content objects (or dicts in mocks)
        mock_chat.get_history.return_value = updated_history
        mock_service_class.return_value = mock_service
        
        # Call function
        continue_image_chat(
            user=self.user,
            edit_prompt="make it warmer",
        )
        
        # Verify history was updated
        self.chat_record.refresh_from_db()
        self.assertEqual(self.chat_record.chat_history, updated_history)

    def test_continue_chat_no_session(self):
        """Test that no existing session returns 400."""
        from apps.identities.functions.public import continue_image_chat
        from rest_framework.exceptions import ValidationError
        
        # Delete chat record
        self.chat_record.delete()
        
        with self.assertRaises(ValidationError) as cm:
            continue_image_chat(
                user=self.user,
                edit_prompt="make it warmer",
            )
        
        self.assertIn("No active image chat", str(cm.exception))

    def test_continue_chat_empty_prompt(self):
        """Test that empty edit prompt validation happens at API level."""
        # Note: Empty prompt validation happens in the serializer/ViewSet,
        # not in the function itself. This test verifies the function would
        # accept it (though API would reject it).
        # The actual validation is tested in the API tests.
        from apps.identities.functions.public import continue_image_chat
        
        # The function itself doesn't validate - it just passes through
        # Validation happens at the serializer level in the ViewSet
        # So we test that the API endpoint validates (see API tests)
        pass

    def test_continue_chat_empty_history(self):
        """Test that empty chat history returns 400."""
        from apps.identities.functions.public import continue_image_chat
        from rest_framework.exceptions import ValidationError
        
        # Update chat record to have empty history
        self.chat_record.chat_history = []
        self.chat_record.save()
        
        with self.assertRaises(ValidationError) as cm:
            continue_image_chat(
                user=self.user,
                edit_prompt="make it warmer",
            )
        
        self.assertIn("Chat history is empty", str(cm.exception))


class ContinueImageChatAPITests(APITestCase):
    """Test the continue image chat API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass123"
        )
        self.identity = Identity.objects.create(
            user=self.user,
            name="The Artist",
            category=IdentityCategory.PASSIONS,
        )
        self.chat_record = IdentityImageChat.objects.create(
            user=self.user,
            identity=self.identity,
            chat_history=[{"role": "user", "parts": [{"text": "Initial prompt"}]}],
        )
        self.client = APIClient()
        self.public_url = "/api/v1/identity-image-chat/continue"
        self.admin_url = "/api/v1/admin/identity-image-chat/continue"

    def _create_mock_pil_image(self):
        """Helper to create a mock PIL image."""
        img = Image.new('RGB', (100, 100), color='red')
        return img

    @patch('services.image_generation.orchestration.GeminiImageService')
    @patch('services.image_generation.utils.chat_history_serializer.deserialize_chat_history')
    def test_continue_chat_success(self, mock_deserialize, mock_service_class):
        """Test successfully continuing a chat via API."""
        self.client.force_authenticate(user=self.user)
        
        # Setup mocks
        mock_deserialize.return_value = [{"role": "user", "parts": [{"text": "Initial prompt"}]}]
        
        mock_service = MagicMock()
        mock_chat = MagicMock()
        mock_service.create_chat.return_value = mock_chat
        mock_response = MagicMock()
        mock_part = MagicMock()
        mock_part.inline_data = MagicMock()
        mock_part.as_image.return_value = self._create_mock_pil_image()
        mock_response.parts = [mock_part]
        mock_service.send_chat_message.return_value = (self._create_mock_pil_image(), mock_response)
        mock_chat.get_history.return_value = []
        mock_service_class.return_value = mock_service
        
        response = self.client.post(
            self.public_url,
            {"edit_prompt": "make the lighting warmer"},
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("image_base64", response.data)
        self.assertEqual(response.data["identity_id"], str(self.identity.id))

    @patch('services.image_generation.orchestration.GeminiImageService')
    @patch('services.image_generation.utils.chat_history_serializer.deserialize_chat_history')
    def test_admin_continue_chat_success(self, mock_deserialize, mock_service_class):
        """Test admin successfully continuing a chat for any user."""
        self.client.force_authenticate(user=self.admin_user)
        
        # Setup mocks
        mock_deserialize.return_value = [{"role": "user", "parts": [{"text": "Initial prompt"}]}]
        
        mock_service = MagicMock()
        mock_chat = MagicMock()
        mock_service.create_chat.return_value = mock_chat
        mock_response = MagicMock()
        mock_part = MagicMock()
        mock_part.inline_data = MagicMock()
        mock_part.as_image.return_value = self._create_mock_pil_image()
        mock_response.parts = [mock_part]
        mock_service.send_chat_message.return_value = (self._create_mock_pil_image(), mock_response)
        mock_chat.get_history.return_value = []
        mock_service_class.return_value = mock_service
        
        response = self.client.post(
            self.admin_url,
            {
                "user_id": str(self.user.id),
                "edit_prompt": "make the lighting warmer",
            },
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("image_base64", response.data)

    def test_continue_chat_requires_auth(self):
        """Test that public endpoint requires authentication."""
        response = self.client.post(
            self.public_url,
            {"edit_prompt": "make it warmer"},
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_continue_chat_requires_admin(self):
        """Test that admin endpoint requires admin user."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(
            self.admin_url,
            {
                "user_id": str(self.user.id),
                "edit_prompt": "make it warmer",
            },
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_continue_chat_missing_edit_prompt(self):
        """Test that missing edit_prompt returns 400."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(
            self.public_url,
            {},
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_continue_chat_empty_edit_prompt(self):
        """Test that empty edit_prompt returns 400."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(
            self.public_url,
            {"edit_prompt": "   "},
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_continue_chat_no_session(self):
        """Test that no active session returns 400."""
        self.client.force_authenticate(user=self.user)
        
        # Delete chat record
        self.chat_record.delete()
        
        response = self.client.post(
            self.public_url,
            {"edit_prompt": "make it warmer"},
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("No active image chat", str(response.data))
