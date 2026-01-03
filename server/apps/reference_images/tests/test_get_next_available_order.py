"""
Tests for get_next_available_order utility function.
"""

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.users.models import User
from apps.reference_images.models import ReferenceImage
from apps.reference_images.utils import get_next_available_order, MAX_REFERENCE_IMAGES


class GetNextAvailableOrderTests(TestCase):
    """Test the get_next_available_order utility function."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

    def test_returns_zero_when_no_images_exist(self):
        """Test that 0 is returned when user has no reference images."""
        result = get_next_available_order(self.user)
        self.assertEqual(result, 0)

    def test_returns_next_available_slot(self):
        """Test that the next available slot is returned when some slots are filled."""
        # Fill slots 0 and 1
        ReferenceImage.objects.create(user=self.user, order=0)
        ReferenceImage.objects.create(user=self.user, order=1)

        result = get_next_available_order(self.user)
        self.assertEqual(result, 2)

    def test_fills_gaps_in_order(self):
        """Test that gaps in the order are filled first."""
        # Fill slots 0 and 2, leaving 1 empty
        ReferenceImage.objects.create(user=self.user, order=0)
        ReferenceImage.objects.create(user=self.user, order=2)

        result = get_next_available_order(self.user)
        self.assertEqual(result, 1)

    def test_raises_error_when_all_slots_filled(self):
        """Test that ValueError is raised when all 5 slots are filled."""
        for i in range(MAX_REFERENCE_IMAGES):
            ReferenceImage.objects.create(user=self.user, order=i)

        with self.assertRaises(ValueError) as context:
            get_next_available_order(self.user)

        self.assertIn(str(MAX_REFERENCE_IMAGES), str(context.exception))

    def test_does_not_consider_other_users_images(self):
        """Test that other users' images don't affect available slots."""
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123"
        )

        # Fill all slots for other user
        for i in range(MAX_REFERENCE_IMAGES):
            ReferenceImage.objects.create(user=other_user, order=i)

        # Current user should still have slot 0 available
        result = get_next_available_order(self.user)
        self.assertEqual(result, 0)

