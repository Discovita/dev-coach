"""
Tests for delete_identity_image utility.
"""

from unittest.mock import MagicMock, patch

from django.test import TestCase

from apps.test_scenario.utils import delete_identity_image


class TestDeleteIdentityImage(TestCase):
    """delete_identity_image tests."""

    # ==================== No-op cases ====================

    def test_no_op_when_no_image_key(self):
        """Should do nothing when identity_data has no 'image' key."""
        with patch("apps.test_scenario.utils.delete_identity_image.default_storage") as mock_storage:
            delete_identity_image({})
            mock_storage.delete.assert_not_called()

    def test_no_op_when_image_is_none(self):
        """Should do nothing when image value is None."""
        with patch("apps.test_scenario.utils.delete_identity_image.default_storage") as mock_storage:
            delete_identity_image({"image": None})
            mock_storage.delete.assert_not_called()

    def test_no_op_when_image_url_yields_no_key(self):
        """Should do nothing when the URL cannot be parsed into an S3 key."""
        with patch(
            "apps.test_scenario.utils.delete_identity_image.extract_s3_key_from_url",
            return_value=None,
        ):
            with patch("apps.test_scenario.utils.delete_identity_image.default_storage") as mock_storage:
                delete_identity_image({"image": "https://unrecognised.example.com/img.jpg"})
                mock_storage.delete.assert_not_called()

    # ==================== Deletion ====================

    def test_deletes_s3_key_extracted_from_url(self):
        """Should call default_storage.delete with the extracted S3 key."""
        with patch(
            "apps.test_scenario.utils.delete_identity_image.extract_s3_key_from_url",
            return_value="media/uuid/photo.jpg",
        ):
            with patch("apps.test_scenario.utils.delete_identity_image.default_storage") as mock_storage:
                delete_identity_image({"image": "https://bucket.s3.amazonaws.com/media/uuid/photo.jpg"})
                mock_storage.delete.assert_called_once_with("media/uuid/photo.jpg")

    def test_swallows_storage_exception(self):
        """Should not raise even when default_storage.delete throws."""
        with patch(
            "apps.test_scenario.utils.delete_identity_image.extract_s3_key_from_url",
            return_value="media/uuid/photo.jpg",
        ):
            with patch("apps.test_scenario.utils.delete_identity_image.default_storage") as mock_storage:
                mock_storage.delete.side_effect = Exception("S3 error")
                # Should not raise
                delete_identity_image({"image": "https://bucket.s3.amazonaws.com/media/uuid/photo.jpg"})
