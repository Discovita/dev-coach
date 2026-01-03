"""
Tests for upload_reference_image function.
"""

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.exceptions import ValidationError

from apps.users.models import User
from apps.reference_images.models import ReferenceImage
from apps.reference_images.functions.public import upload_reference_image


class UploadReferenceImageTests(TestCase):
    """Test the upload_reference_image function."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.ref_image = ReferenceImage.objects.create(
            user=self.user,
            name="Test Image",
            order=0
        )

    def _create_test_image(self, name="test.jpg"):
        """Helper to create a test image file."""
        return SimpleUploadedFile(
            name=name,
            content=b"\x47\x49\x46\x38\x89\x61",  # Minimal GIF header
            content_type="image/gif"
        )

    def test_uploads_image_to_empty_slot(self):
        """Test that an image can be uploaded to an empty reference image."""
        image_file = self._create_test_image()

        updated = upload_reference_image(
            reference_image=self.ref_image,
            image_file=image_file
        )

        self.assertTrue(updated.image)
        self.assertEqual(updated.id, self.ref_image.id)

    def test_replaces_existing_image(self):
        """Test that uploading replaces an existing image."""
        # First upload
        image_file1 = self._create_test_image("image1.jpg")
        upload_reference_image(
            reference_image=self.ref_image,
            image_file=image_file1
        )
        first_url = self.ref_image.image.url if self.ref_image.image else None

        # Second upload
        image_file2 = self._create_test_image("image2.jpg")
        updated = upload_reference_image(
            reference_image=self.ref_image,
            image_file=image_file2
        )

        self.assertTrue(updated.image)
        # The image should be different (new upload)
        self.assertNotEqual(first_url, updated.image.url)

    def test_raises_error_when_no_file_provided(self):
        """Test that ValidationError is raised when no file is provided."""
        with self.assertRaises(ValidationError) as context:
            upload_reference_image(
                reference_image=self.ref_image,
                image_file=None
            )

        self.assertIn("No image file provided", str(context.exception.detail))

    def test_returns_updated_reference_image(self):
        """Test that the function returns the updated ReferenceImage instance."""
        image_file = self._create_test_image()

        result = upload_reference_image(
            reference_image=self.ref_image,
            image_file=image_file
        )

        self.assertIsInstance(result, ReferenceImage)
        self.assertEqual(result.id, self.ref_image.id)

