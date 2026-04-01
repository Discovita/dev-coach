"""
Tests for delete_removed_identity_images utility.
"""

from unittest.mock import patch

from django.test import TestCase

from apps.test_scenario.utils import delete_removed_identity_images


class TestDeleteRemovedIdentityImages(TestCase):
    """delete_removed_identity_images tests."""

    # ==================== No-op cases ====================

    def test_no_op_when_old_template_is_none(self):
        """Should do nothing when old_template is None."""
        template = {"identities": [{"name": "Explorer"}]}
        with patch("apps.test_scenario.utils.delete_removed_identity_images.default_storage") as mock_storage:
            delete_removed_identity_images(template, None)
            mock_storage.delete.assert_not_called()

    def test_no_op_when_old_template_has_no_identities(self):
        """Should do nothing when old_template has no 'identities' key."""
        template = {"identities": [{"name": "Explorer"}]}
        old_template = {"user": {"first_name": "Test", "last_name": "User"}}
        with patch("apps.test_scenario.utils.delete_removed_identity_images.default_storage") as mock_storage:
            delete_removed_identity_images(template, old_template)
            mock_storage.delete.assert_not_called()

    def test_no_op_when_image_still_present(self):
        """Should not delete when both old and new identity have the same image."""
        url = "https://bucket.s3.amazonaws.com/media/uuid/photo.jpg"
        template = {"identities": [{"name": "Explorer", "image": url}]}
        old_template = {"identities": [{"name": "Explorer", "image": url}]}
        with patch("apps.test_scenario.utils.delete_removed_identity_images.default_storage") as mock_storage:
            delete_removed_identity_images(template, old_template)
            mock_storage.delete.assert_not_called()

    def test_no_op_when_old_identity_had_no_image(self):
        """Should not delete when old identity had no image."""
        template = {"identities": [{"name": "Explorer"}]}
        old_template = {"identities": [{"name": "Explorer"}]}
        with patch("apps.test_scenario.utils.delete_removed_identity_images.default_storage") as mock_storage:
            delete_removed_identity_images(template, old_template)
            mock_storage.delete.assert_not_called()

    # ==================== Deletion ====================

    def test_deletes_image_when_removed_from_new_template(self):
        """Should delete S3 object when an identity's image was removed."""
        old_url = "https://bucket.s3.amazonaws.com/media/uuid/photo.jpg"
        template = {"identities": [{"name": "Explorer"}]}
        old_template = {"identities": [{"name": "Explorer", "image": old_url}]}
        with patch(
            "apps.test_scenario.utils.delete_removed_identity_images.extract_s3_key_from_url",
            return_value="media/uuid/photo.jpg",
        ):
            with patch("apps.test_scenario.utils.delete_removed_identity_images.default_storage") as mock_storage:
                delete_removed_identity_images(template, old_template)
                mock_storage.delete.assert_called_once_with("media/uuid/photo.jpg")

    def test_swallows_storage_exception(self):
        """Should not raise even when default_storage.delete throws."""
        old_url = "https://bucket.s3.amazonaws.com/media/uuid/photo.jpg"
        template = {"identities": [{"name": "Explorer"}]}
        old_template = {"identities": [{"name": "Explorer", "image": old_url}]}
        with patch(
            "apps.test_scenario.utils.delete_removed_identity_images.extract_s3_key_from_url",
            return_value="media/uuid/photo.jpg",
        ):
            with patch("apps.test_scenario.utils.delete_removed_identity_images.default_storage") as mock_storage:
                mock_storage.delete.side_effect = Exception("S3 error")
                # Should not raise
                delete_removed_identity_images(template, old_template)

    def test_handles_new_template_having_fewer_identities(self):
        """Should stop comparing when new template has fewer identities than old."""
        old_url = "https://bucket.s3.amazonaws.com/media/uuid/photo.jpg"
        template = {"identities": []}
        old_template = {"identities": [{"name": "Explorer", "image": old_url}]}
        with patch("apps.test_scenario.utils.delete_removed_identity_images.default_storage") as mock_storage:
            # Should not raise an IndexError
            delete_removed_identity_images(template, old_template)
