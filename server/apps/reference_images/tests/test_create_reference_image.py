"""
Tests for create_reference_image function.
"""

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.exceptions import ValidationError

from apps.users.models import User
from apps.reference_images.models import ReferenceImage
from apps.reference_images.functions.public import create_reference_image
from apps.reference_images.utils import MAX_REFERENCE_IMAGES


class CreateReferenceImageTests(TestCase):
    """Test the create_reference_image function."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

    def test_creates_reference_image_with_default_order(self):
        """Test that a reference image is created with auto-assigned order."""
        ref_image = create_reference_image(user=self.user)

        self.assertIsNotNone(ref_image.id)
        self.assertEqual(ref_image.user, self.user)
        self.assertEqual(ref_image.order, 0)
        self.assertEqual(ref_image.name, "")

    def test_creates_reference_image_with_name(self):
        """Test that a reference image can be created with a name."""
        ref_image = create_reference_image(user=self.user, name="Headshot 1")

        self.assertEqual(ref_image.name, "Headshot 1")

    def test_creates_reference_image_with_specific_order(self):
        """Test that a reference image can be created with a specific order."""
        ref_image = create_reference_image(user=self.user, order=3)

        self.assertEqual(ref_image.order, 3)

    def test_auto_assigns_next_available_order(self):
        """Test that order is auto-assigned to next available slot."""
        create_reference_image(user=self.user, order=0)
        ref_image = create_reference_image(user=self.user)

        self.assertEqual(ref_image.order, 1)

    def test_raises_error_when_order_already_in_use(self):
        """Test that ValidationError is raised when order is already used."""
        create_reference_image(user=self.user, order=2)

        with self.assertRaises(ValidationError) as context:
            create_reference_image(user=self.user, order=2)

        self.assertIn("already in use", str(context.exception.detail))

    def test_raises_error_when_order_out_of_range_negative(self):
        """Test that ValidationError is raised for negative order."""
        with self.assertRaises(ValidationError) as context:
            create_reference_image(user=self.user, order=-1)

        self.assertIn("Order must be between", str(context.exception.detail))

    def test_raises_error_when_order_out_of_range_too_high(self):
        """Test that ValidationError is raised for order >= MAX_REFERENCE_IMAGES."""
        with self.assertRaises(ValidationError) as context:
            create_reference_image(user=self.user, order=MAX_REFERENCE_IMAGES)

        self.assertIn("Order must be between", str(context.exception.detail))

    def test_raises_error_when_max_images_reached(self):
        """Test that ValidationError is raised when user has 5 images."""
        for i in range(MAX_REFERENCE_IMAGES):
            create_reference_image(user=self.user, order=i)

        with self.assertRaises(ValidationError) as context:
            create_reference_image(user=self.user)

        self.assertIn(str(MAX_REFERENCE_IMAGES), str(context.exception.detail))

    def test_creates_image_with_file(self):
        """Test that reference image can be created with an image file."""
        # Create a simple test image file
        image_file = SimpleUploadedFile(
            name="test_image.jpg",
            content=b"\x47\x49\x46\x38\x89\x61",  # Minimal GIF header
            content_type="image/gif"
        )

        ref_image = create_reference_image(
            user=self.user,
            name="Test Image",
            image_file=image_file
        )

        self.assertIsNotNone(ref_image.id)
        self.assertTrue(ref_image.image)

    def test_different_users_can_use_same_order(self):
        """Test that different users can have images at the same order."""
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123"
        )

        ref_image1 = create_reference_image(user=self.user, order=0)
        ref_image2 = create_reference_image(user=other_user, order=0)

        self.assertEqual(ref_image1.order, 0)
        self.assertEqual(ref_image2.order, 0)
        self.assertNotEqual(ref_image1.id, ref_image2.id)

