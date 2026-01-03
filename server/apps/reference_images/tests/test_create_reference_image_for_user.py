"""
Tests for create_reference_image_for_user admin function.
"""

from django.test import TestCase
from rest_framework.exceptions import NotFound, ValidationError

from apps.users.models import User
from apps.reference_images.models import ReferenceImage
from apps.reference_images.functions.admin import create_reference_image_for_user
from apps.reference_images.utils import MAX_REFERENCE_IMAGES
import uuid


class CreateReferenceImageForUserTests(TestCase):
    """Test the create_reference_image_for_user admin function."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

    def test_creates_reference_image_for_valid_user(self):
        """Test that a reference image is created for a valid user ID."""
        ref_image = create_reference_image_for_user(
            user_id=self.user.id,
            name="Admin Created"
        )

        self.assertIsNotNone(ref_image.id)
        self.assertEqual(ref_image.user, self.user)
        self.assertEqual(ref_image.name, "Admin Created")

    def test_raises_not_found_for_invalid_user_id(self):
        """Test that NotFound is raised for non-existent user ID."""
        fake_user_id = uuid.uuid4()

        with self.assertRaises(NotFound) as context:
            create_reference_image_for_user(user_id=fake_user_id)

        self.assertIn("not found", str(context.exception.detail).lower())

    def test_can_specify_order(self):
        """Test that a specific order can be provided."""
        ref_image = create_reference_image_for_user(
            user_id=self.user.id,
            order=3
        )

        self.assertEqual(ref_image.order, 3)

    def test_auto_assigns_order_when_not_specified(self):
        """Test that order is auto-assigned when not specified."""
        ref_image1 = create_reference_image_for_user(user_id=self.user.id)
        ref_image2 = create_reference_image_for_user(user_id=self.user.id)

        self.assertEqual(ref_image1.order, 0)
        self.assertEqual(ref_image2.order, 1)

    def test_respects_max_images_limit(self):
        """Test that ValidationError is raised when user has 5 images."""
        for i in range(MAX_REFERENCE_IMAGES):
            create_reference_image_for_user(user_id=self.user.id, order=i)

        with self.assertRaises(ValidationError):
            create_reference_image_for_user(user_id=self.user.id)

