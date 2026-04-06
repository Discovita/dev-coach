"""
Tests for gather_identities_section function.
"""

from unittest.mock import patch

from django.test import TestCase

from apps.identities.models import Identity
from apps.test_scenario.utils import gather_identities_section
from apps.users.models import User


class TestGatherIdentitiesSection(TestCase):
    """gather_identities_section tests."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="gather_id@example.com", password="testpass"
        )

    # ==================== Empty case ====================

    def test_returns_empty_list_when_no_identities(self):
        """Should return an empty list when the user has no identities."""
        result = gather_identities_section(self.user)
        self.assertEqual(result, [])

    # ==================== Basic output ====================

    def test_entry_contains_name_and_category(self):
        """Each entry should always contain name and category."""
        Identity.objects.create(
            user=self.user, name="Explorer", category="PASSIONS"
        )
        result = gather_identities_section(self.user)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Explorer")
        self.assertEqual(result[0]["category"], "PASSIONS")

    def test_optional_fields_included_when_present(self):
        """Should include state, i_am_statement, visualization, notes when set."""
        Identity.objects.create(
            user=self.user,
            name="Explorer",
            category="PASSIONS",
            state="ACCEPTED",
            i_am_statement="I am an explorer.",
            visualization="A vivid scene.",
            notes=["note1"],
        )
        result = gather_identities_section(self.user)
        entry = result[0]
        self.assertEqual(entry["state"], "ACCEPTED")
        self.assertEqual(entry["i_am_statement"], "I am an explorer.")
        self.assertEqual(entry["visualization"], "A vivid scene.")
        self.assertEqual(entry["notes"], ["note1"])

    def test_optional_text_fields_omitted_when_absent(self):
        """Should omit i_am_statement, visualization, and notes when falsy."""
        Identity.objects.create(
            user=self.user, name="Explorer", category="PASSIONS",
            # state has a model default of PROPOSED, so it will be included
            i_am_statement="",
            visualization="",
            notes=[],
        )
        result = gather_identities_section(self.user)
        entry = result[0]
        self.assertNotIn("i_am_statement", entry)
        self.assertNotIn("visualization", entry)
        self.assertNotIn("notes", entry)

    def test_state_included_when_set_to_default(self):
        """State is always included because the model defaults to PROPOSED."""
        Identity.objects.create(
            user=self.user, name="Explorer", category="PASSIONS"
        )
        result = gather_identities_section(self.user)
        # Default state is 'proposed' which is truthy, so it is captured
        self.assertIn("state", result[0])

    # ==================== Image duplication ====================

    def test_image_omitted_when_identity_has_no_image(self):
        """Should not include 'image' key when identity has no image."""
        Identity.objects.create(
            user=self.user, name="Explorer", category="PASSIONS"
        )
        result = gather_identities_section(self.user)
        self.assertNotIn("image", result[0])

    def test_image_included_when_duplicate_succeeds(self):
        """Should include image URL when duplicate_s3_image returns a key."""
        identity = Identity.objects.create(
            user=self.user, name="Explorer", category="PASSIONS"
        )
        # Give the identity a fake image
        identity.image.name = "media/uuid/photo.jpg"
        identity.save()

        with patch(
            "apps.test_scenario.utils.gather_identities_section.duplicate_s3_image",
            return_value="media/new-uuid/photo.jpg",
        ):
            with patch(
                "apps.test_scenario.utils.gather_identities_section.default_storage"
            ) as mock_storage:
                mock_storage.url.return_value = "https://bucket.s3.amazonaws.com/media/new-uuid/photo.jpg"
                result = gather_identities_section(self.user)

        self.assertIn("image", result[0])
        self.assertEqual(
            result[0]["image"],
            "https://bucket.s3.amazonaws.com/media/new-uuid/photo.jpg",
        )

    def test_image_omitted_when_duplicate_fails(self):
        """Should omit image when duplicate_s3_image returns None."""
        identity = Identity.objects.create(
            user=self.user, name="Explorer", category="PASSIONS"
        )
        identity.image.name = "media/uuid/photo.jpg"
        identity.save()

        with patch(
            "apps.test_scenario.utils.gather_identities_section.duplicate_s3_image",
            return_value=None,
        ):
            result = gather_identities_section(self.user)

        self.assertNotIn("image", result[0])

    # ==================== Multi-user isolation ====================

    def test_does_not_return_other_users_identities(self):
        """Should only return identities for the specified user."""
        other = User.objects.create_user(
            email="other_gather_id@example.com", password="testpass"
        )
        Identity.objects.create(user=other, name="Other", category="PASSIONS")
        result = gather_identities_section(self.user)
        self.assertEqual(result, [])
