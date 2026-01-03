"""
Tests for ReferenceImageViewSet API endpoints.
"""

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.users.models import User
from apps.reference_images.models import ReferenceImage
from apps.reference_images.utils import MAX_REFERENCE_IMAGES


class ReferenceImageViewSetTests(APITestCase):
    """Test the ReferenceImageViewSet API endpoints."""

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
        self.client = APIClient()
        self.base_url = "/api/v1/reference-images"

    def _create_test_image(self, name="test.jpg"):
        """Helper to create a test image file."""
        return SimpleUploadedFile(
            name=name,
            content=b"\x47\x49\x46\x38\x89\x61",
            content_type="image/gif"
        )

    # ========== LIST TESTS ==========

    def test_list_returns_own_images(self):
        """Test that list returns only the current user's images."""
        self.client.force_authenticate(user=self.user)
        ReferenceImage.objects.create(user=self.user, order=0)
        ReferenceImage.objects.create(user=self.user, order=1)

        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_does_not_return_other_users_images(self):
        """Test that list doesn't return other users' images."""
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        ReferenceImage.objects.create(user=self.user, order=0)
        ReferenceImage.objects.create(user=other_user, order=0)

        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_requires_authentication(self):
        """Test that list requires authentication."""
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_list_other_users_images(self):
        """Test that admin can list another user's images with user_id param."""
        self.client.force_authenticate(user=self.admin_user)
        ReferenceImage.objects.create(user=self.user, order=0)

        response = self.client.get(f"{self.base_url}?user_id={self.user.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_non_admin_ignores_user_id_param(self):
        """Test that non-admin user_id param is ignored."""
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        ReferenceImage.objects.create(user=other_user, order=0)

        response = self.client.get(f"{self.base_url}?user_id={other_user.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return current user's images (none), not other user's
        self.assertEqual(len(response.data), 0)

    # ========== CREATE TESTS ==========

    def test_create_reference_image(self):
        """Test creating a new reference image."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.base_url,
            {"name": "My Headshot"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "My Headshot")
        self.assertEqual(response.data["order"], 0)

    def test_create_with_specific_order(self):
        """Test creating a reference image with a specific order."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.base_url,
            {"name": "Image 3", "order": 2},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["order"], 2)

    def test_create_with_image_file(self):
        """Test creating a reference image with an uploaded file."""
        self.client.force_authenticate(user=self.user)
        image_file = self._create_test_image()

        response = self.client.post(
            self.base_url,
            {"name": "Photo", "image": image_file},
            format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Verify image was saved by checking the database
        ref_image = ReferenceImage.objects.get(id=response.data["id"])
        self.assertTrue(ref_image.image)

    def test_create_fails_when_max_reached(self):
        """Test that create fails when user has max images."""
        self.client.force_authenticate(user=self.user)

        for i in range(MAX_REFERENCE_IMAGES):
            ReferenceImage.objects.create(user=self.user, order=i)

        response = self.client.post(
            self.base_url,
            {"name": "One Too Many"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_can_create_for_other_user(self):
        """Test that admin can create image for another user."""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(
            self.base_url,
            {"user_id": str(self.user.id), "name": "Admin Created"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Admin Created")

        # Verify the image belongs to the target user
        ref_image = ReferenceImage.objects.get(id=response.data["id"])
        self.assertEqual(ref_image.user, self.user)

    # ========== RETRIEVE TESTS ==========

    def test_retrieve_own_image(self):
        """Test retrieving a specific reference image."""
        self.client.force_authenticate(user=self.user)
        ref_image = ReferenceImage.objects.create(user=self.user, name="Test", order=0)

        response = self.client.get(f"{self.base_url}/{ref_image.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test")

    def test_cannot_retrieve_other_users_image(self):
        """Test that user cannot retrieve another user's image."""
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        ref_image = ReferenceImage.objects.create(user=other_user, order=0)

        response = self.client.get(f"{self.base_url}/{ref_image.id}")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ========== UPDATE TESTS ==========

    def test_update_reference_image_name(self):
        """Test updating a reference image's name."""
        self.client.force_authenticate(user=self.user)
        ref_image = ReferenceImage.objects.create(user=self.user, name="Old Name", order=0)

        response = self.client.patch(
            f"{self.base_url}/{ref_image.id}",
            {"name": "New Name"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "New Name")

    # ========== DELETE TESTS ==========

    def test_delete_reference_image(self):
        """Test deleting a reference image."""
        self.client.force_authenticate(user=self.user)
        ref_image = ReferenceImage.objects.create(user=self.user, order=0)

        response = self.client.delete(f"{self.base_url}/{ref_image.id}")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ReferenceImage.objects.filter(id=ref_image.id).exists())

    def test_cannot_delete_other_users_image(self):
        """Test that user cannot delete another user's image."""
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        ref_image = ReferenceImage.objects.create(user=other_user, order=0)

        response = self.client.delete(f"{self.base_url}/{ref_image.id}")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(ReferenceImage.objects.filter(id=ref_image.id).exists())

    # ========== UPLOAD IMAGE TESTS ==========

    def test_upload_image_action(self):
        """Test the upload-image action endpoint."""
        self.client.force_authenticate(user=self.user)
        ref_image = ReferenceImage.objects.create(user=self.user, order=0)
        image_file = self._create_test_image()

        response = self.client.post(
            f"{self.base_url}/{ref_image.id}/upload-image",
            {"image": image_file},
            format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify image was saved by checking the database
        ref_image.refresh_from_db()
        self.assertTrue(ref_image.image)

    def test_upload_image_fails_without_file(self):
        """Test that upload-image fails without a file."""
        self.client.force_authenticate(user=self.user)
        ref_image = ReferenceImage.objects.create(user=self.user, order=0)

        response = self.client.post(
            f"{self.base_url}/{ref_image.id}/upload-image",
            {},
            format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

