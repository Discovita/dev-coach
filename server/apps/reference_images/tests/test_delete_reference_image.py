"""
Tests for delete_reference_image function.
"""

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.users.models import User
from apps.reference_images.models import ReferenceImage
from apps.reference_images.functions.public import delete_reference_image


class DeleteReferenceImageTests(TestCase):
    """Test the delete_reference_image function."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

    def test_deletes_reference_image_without_file(self):
        """Test that a reference image without a file is deleted."""
        ref_image = ReferenceImage.objects.create(
            user=self.user,
            name="Test Image",
            order=0
        )
        ref_image_id = ref_image.id

        delete_reference_image(ref_image)

        self.assertFalse(ReferenceImage.objects.filter(id=ref_image_id).exists())

    def test_deletes_reference_image_with_file(self):
        """Test that a reference image with a file is deleted."""
        image_file = SimpleUploadedFile(
            name="test.jpg",
            content=b"\x47\x49\x46\x38\x89\x61",
            content_type="image/gif"
        )
        ref_image = ReferenceImage.objects.create(
            user=self.user,
            name="Test Image",
            order=0
        )
        ref_image.image = image_file
        ref_image.save()
        ref_image_id = ref_image.id

        delete_reference_image(ref_image)

        self.assertFalse(ReferenceImage.objects.filter(id=ref_image_id).exists())

    def test_does_not_affect_other_images(self):
        """Test that deleting one image doesn't affect others."""
        ref_image1 = ReferenceImage.objects.create(
            user=self.user,
            name="Image 1",
            order=0
        )
        ref_image2 = ReferenceImage.objects.create(
            user=self.user,
            name="Image 2",
            order=1
        )

        delete_reference_image(ref_image1)

        self.assertFalse(ReferenceImage.objects.filter(id=ref_image1.id).exists())
        self.assertTrue(ReferenceImage.objects.filter(id=ref_image2.id).exists())

    def test_frees_up_order_slot(self):
        """Test that deleting an image frees up the order slot for reuse."""
        ref_image = ReferenceImage.objects.create(
            user=self.user,
            order=2
        )

        delete_reference_image(ref_image)

        # Should be able to create a new image at the same order
        new_ref_image = ReferenceImage.objects.create(
            user=self.user,
            order=2
        )
        self.assertEqual(new_ref_image.order, 2)

