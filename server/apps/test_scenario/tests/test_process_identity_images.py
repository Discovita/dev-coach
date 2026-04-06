"""
Tests for apps.test_scenario.utils.process_identity_images.

Verifies image file processing from request.FILES, S3 upload,
and deletion of removed identity images.
"""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.test_scenario.utils.process_identity_images import process_identity_images


def _make_request_with_files(files_dict):
    """Build a mock request whose FILES attribute behaves like a MultiValueDict."""
    request = MagicMock()
    mock_files = MagicMock()
    mock_files.__bool__ = MagicMock(return_value=bool(files_dict))
    mock_files.__contains__ = lambda self, k: k in files_dict
    mock_files.__getitem__ = lambda self, k: files_dict[k]
    mock_files.keys = MagicMock(return_value=files_dict.keys())
    mock_files.get = lambda k, d=None: files_dict.get(k, d)
    request.FILES = mock_files
    return request


class ProcessIdentityImagesTests(SimpleTestCase):
    """Tests for process_identity_images utility."""

    def test_returns_template_unchanged_when_no_identities(self):
        """Should return template as-is if no identities key."""
        request = MagicMock()
        template = {"some_key": "value"}
        result = process_identity_images(request, template)
        self.assertEqual(result, template)

    def test_returns_template_unchanged_when_identities_empty(self):
        """Should return template as-is if identities list is empty."""
        request = MagicMock()
        template = {"identities": []}
        result = process_identity_images(request, template)
        self.assertEqual(result, template)

    @patch(
        "apps.test_scenario.utils.process_identity_images.delete_removed_identity_images"
    )
    def test_calls_delete_removed_with_old_template(self, mock_delete):
        """Should call delete_removed_identity_images with old template."""
        request = _make_request_with_files({})
        template = {"identities": [{"name": "Test"}]}
        old_template = {"identities": [{"name": "Old", "image": "url"}]}

        process_identity_images(request, template, old_template)

        mock_delete.assert_called_once_with(template, old_template)

    @patch(
        "apps.test_scenario.utils.process_identity_images.delete_removed_identity_images"
    )
    def test_no_files_returns_template(self, mock_delete):
        """Should return template unchanged when no files uploaded."""
        request = _make_request_with_files({})
        template = {"identities": [{"name": "Test"}]}

        result = process_identity_images(request, template)
        self.assertEqual(result, template)

    @patch(
        "apps.test_scenario.utils.process_identity_images.delete_removed_identity_images"
    )
    @patch(
        "apps.test_scenario.utils.process_identity_images.delete_identity_image"
    )
    @patch(
        "apps.test_scenario.utils.process_identity_images.default_storage"
    )
    def test_uploads_image_and_sets_url(
        self, mock_storage, mock_delete_img, mock_delete_removed
    ):
        """Should upload image file and set URL on identity."""
        mock_file = MagicMock()
        mock_file.name = "photo.jpg"
        request = _make_request_with_files({"identity_0_image": mock_file})
        template = {"identities": [{"name": "Visionary"}]}

        mock_storage.save.return_value = "uuid/photo.jpg"
        mock_storage.url.return_value = "https://s3.example.com/uuid/photo.jpg"

        result = process_identity_images(request, template)

        mock_storage.save.assert_called_once()
        self.assertEqual(
            result["identities"][0]["image"],
            "https://s3.example.com/uuid/photo.jpg",
        )

    @patch(
        "apps.test_scenario.utils.process_identity_images.delete_removed_identity_images"
    )
    @patch(
        "apps.test_scenario.utils.process_identity_images.delete_identity_image"
    )
    @patch(
        "apps.test_scenario.utils.process_identity_images.default_storage"
    )
    def test_deletes_existing_image_before_upload(
        self, mock_storage, mock_delete_img, mock_delete_removed
    ):
        """Should call delete_identity_image before uploading new image."""
        mock_file = MagicMock()
        mock_file.name = "new.jpg"
        request = _make_request_with_files({"identity_0_image": mock_file})
        template = {"identities": [{"name": "Test", "image": "old_url"}]}

        mock_storage.save.return_value = "path"
        mock_storage.url.return_value = "url"

        process_identity_images(request, template)

        mock_delete_img.assert_called_once_with(template["identities"][0])

    @patch(
        "apps.test_scenario.utils.process_identity_images.delete_removed_identity_images"
    )
    def test_skips_out_of_range_index(self, mock_delete_removed):
        """Should skip image files with index beyond identities list."""
        mock_file = MagicMock()
        mock_file.name = "photo.jpg"
        request = _make_request_with_files({"identity_5_image": mock_file})
        template = {"identities": [{"name": "Only one"}]}

        result = process_identity_images(request, template)
        self.assertNotIn("image", result["identities"][0])

    @patch(
        "apps.test_scenario.utils.process_identity_images.delete_removed_identity_images"
    )
    def test_ignores_non_identity_files(self, mock_delete_removed):
        """Should ignore files that don't match identity_N_image pattern."""
        request = _make_request_with_files({"avatar": MagicMock()})
        template = {"identities": [{"name": "Test"}]}

        result = process_identity_images(request, template)
        self.assertNotIn("image", result["identities"][0])
