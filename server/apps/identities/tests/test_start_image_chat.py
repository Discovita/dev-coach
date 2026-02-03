"""
Tests for start image chat endpoints and functions.
"""

from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from PIL import Image
import io

from apps.users.models import User
from apps.identities.models import Identity, IdentityImageChat
from apps.reference_images.models import ReferenceImage
from enums.identity_category import IdentityCategory


class StartImageChatFunctionTests(TestCase):
    """Test the start_image_chat function directly."""

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
        # Create a reference image
        self.reference_image = ReferenceImage.objects.create(
            user=self.user,
            order=0,
        )

    def _create_mock_pil_image(self):
        """Helper to create a mock PIL image."""
        img = Image.new('RGB', (100, 100), color='red')
        return img

    @patch('services.image_generation.orchestration.GeminiImageService')
    @patch('services.image_generation.orchestration.load_pil_images_from_references')
    @patch('services.image_generation.orchestration.PromptManager')
    def test_start_chat_success(self, mock_prompt_manager, mock_load_images, mock_service_class):
        """Test successfully starting a chat and returning image."""
        from apps.identities.functions.public import start_image_chat
        
        # Setup mocks
        mock_prompt_manager.return_value.create_image_generation_prompt.return_value = "Generate an image"
        mock_load_images.return_value = [self._create_mock_pil_image()]
        
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
        
        # Call function
        response = start_image_chat(
            user=self.user,
            identity_id=str(self.identity.id),
            additional_prompt="",
        )
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("image_base64", response.data)
        self.assertEqual(response.data["identity_id"], str(self.identity.id))
        self.assertEqual(response.data["identity_name"], self.identity.name)
        
        # Verify chat record was created
        self.assertTrue(IdentityImageChat.objects.filter(user=self.user).exists())

    @patch('services.image_generation.orchestration.GeminiImageService')
    @patch('services.image_generation.orchestration.load_pil_images_from_references')
    @patch('services.image_generation.orchestration.PromptManager')
    def test_start_chat_creates_record(self, mock_prompt_manager, mock_load_images, mock_service_class):
        """Test that starting a chat creates IdentityImageChat record."""
        from apps.identities.functions.public import start_image_chat
        
        # Setup mocks
        mock_prompt_manager.return_value.create_image_generation_prompt.return_value = "Generate an image"
        mock_load_images.return_value = [self._create_mock_pil_image()]
        
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
        
        # Verify no chat record exists
        self.assertFalse(IdentityImageChat.objects.filter(user=self.user).exists())
        
        # Call function
        start_image_chat(
            user=self.user,
            identity_id=str(self.identity.id),
            additional_prompt="",
        )
        
        # Verify chat record was created
        chat_record = IdentityImageChat.objects.get(user=self.user)
        self.assertEqual(chat_record.identity, self.identity)

    @patch('services.image_generation.orchestration.GeminiImageService')
    @patch('services.image_generation.orchestration.load_pil_images_from_references')
    @patch('services.image_generation.orchestration.PromptManager')
    def test_start_chat_replaces_existing(self, mock_prompt_manager, mock_load_images, mock_service_class):
        """Test that starting a new chat replaces existing."""
        from apps.identities.functions.public import start_image_chat
        
        # Create existing chat
        old_chat = IdentityImageChat.objects.create(
            user=self.user,
            identity=self.identity,
            chat_history=[{"old": "data"}],
        )
        
        # Setup mocks
        mock_prompt_manager.return_value.create_image_generation_prompt.return_value = "Generate an image"
        mock_load_images.return_value = [self._create_mock_pil_image()]
        
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
        new_history = [{"role": "user", "parts": [{"text": "Initial prompt"}]}]
        mock_chat.get_history.return_value = new_history
        mock_service_class.return_value = mock_service
        
        # Call function
        start_image_chat(
            user=self.user,
            identity_id=str(self.identity.id),
            additional_prompt="",
        )
        
        # Verify old chat was replaced (same ID, new history)
        old_chat.refresh_from_db()
        self.assertEqual(old_chat.chat_history, new_history)
        # Should still be only one chat record
        self.assertEqual(IdentityImageChat.objects.filter(user=self.user).count(), 1)

    def test_start_chat_missing_identity(self):
        """Test that missing identity returns 404."""
        from apps.identities.functions.public import start_image_chat
        from rest_framework.exceptions import NotFound
        
        with self.assertRaises(NotFound):
            start_image_chat(
                user=self.user,
                identity_id="00000000-0000-0000-0000-000000000000",
                additional_prompt="",
            )

    def test_start_chat_no_reference_images(self):
        """Test that no reference images returns 400."""
        from apps.identities.functions.public import start_image_chat
        from rest_framework.exceptions import ValidationError
        
        # Delete reference image
        self.reference_image.delete()
        
        with self.assertRaises(ValidationError) as cm:
            start_image_chat(
                user=self.user,
                identity_id=str(self.identity.id),
                additional_prompt="",
            )
        
        self.assertIn("No reference images", str(cm.exception))


class StartImageChatAPITests(APITestCase):
    """Test the start image chat API endpoints."""

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
        self.reference_image = ReferenceImage.objects.create(
            user=self.user,
            order=0,
        )
        self.client = APIClient()
        self.public_url = "/api/v1/identity-image-chat/start"
        self.admin_url = "/api/v1/admin/identity-image-chat/start"

    def _create_mock_pil_image(self):
        """Helper to create a mock PIL image."""
        img = Image.new('RGB', (100, 100), color='red')
        return img

    @patch('services.image_generation.orchestration.GeminiImageService')
    @patch('services.image_generation.orchestration.load_pil_images_from_references')
    @patch('services.image_generation.orchestration.PromptManager')
    def test_start_chat_success(self, mock_prompt_manager, mock_load_images, mock_service_class):
        """Test successfully starting a chat via API."""
        self.client.force_authenticate(user=self.user)
        
        # Setup mocks
        mock_prompt_manager.return_value.create_image_generation_prompt.return_value = "Generate an image"
        mock_load_images.return_value = [self._create_mock_pil_image()]
        
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
            {"identity_id": str(self.identity.id)},
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("image_base64", response.data)
        self.assertEqual(response.data["identity_id"], str(self.identity.id))

    @patch('services.image_generation.orchestration.GeminiImageService')
    @patch('services.image_generation.orchestration.load_pil_images_from_references')
    @patch('services.image_generation.orchestration.PromptManager')
    def test_admin_start_chat_success(self, mock_prompt_manager, mock_load_images, mock_service_class):
        """Test admin successfully starting a chat for any user."""
        self.client.force_authenticate(user=self.admin_user)
        
        # Setup mocks
        mock_prompt_manager.return_value.create_image_generation_prompt.return_value = "Generate an image"
        mock_load_images.return_value = [self._create_mock_pil_image()]
        
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
                "identity_id": str(self.identity.id),
                "user_id": str(self.user.id),
            },
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("image_base64", response.data)

    def test_start_chat_requires_auth(self):
        """Test that public endpoint requires authentication."""
        response = self.client.post(
            self.public_url,
            {"identity_id": str(self.identity.id)},
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_start_chat_requires_admin(self):
        """Test that admin endpoint requires admin user."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(
            self.admin_url,
            {
                "identity_id": str(self.identity.id),
                "user_id": str(self.user.id),
            },
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_start_chat_missing_identity_id(self):
        """Test that missing identity_id returns 400."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(
            self.public_url,
            {},
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
