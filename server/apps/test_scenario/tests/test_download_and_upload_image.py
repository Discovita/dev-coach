"""
Tests for download_and_upload_image utility.
"""

from unittest.mock import MagicMock, patch

from django.test import TestCase

from apps.test_scenario.utils import download_and_upload_image


class TestDownloadAndUploadImage(TestCase):
    """download_and_upload_image tests."""

    def _make_response(self, content=b"image-data", content_type="image/jpeg", status=200):
        mock_resp = MagicMock()
        mock_resp.content = content
        mock_resp.headers = {"content-type": content_type}
        mock_resp.raise_for_status = MagicMock()
        if status != 200:
            from requests import HTTPError
            mock_resp.raise_for_status.side_effect = HTTPError("Not OK")
        return mock_resp

    # ==================== Success cases ====================

    def test_saves_downloaded_image_to_storage(self):
        """Should call default_storage.save with the downloaded content."""
        with patch(
            "apps.test_scenario.utils.download_and_upload_image.requests.get",
            return_value=self._make_response(),
        ):
            with patch(
                "apps.test_scenario.utils.download_and_upload_image.default_storage"
            ) as mock_storage:
                mock_storage.save.return_value = "uuid/photo.jpg"
                result = download_and_upload_image("https://example.com/photo.jpg")

        mock_storage.save.assert_called_once()
        self.assertEqual(result, "uuid/photo.jpg")

    def test_uses_filename_from_url(self):
        """Should extract filename from the URL path."""
        with patch(
            "apps.test_scenario.utils.download_and_upload_image.requests.get",
            return_value=self._make_response(),
        ):
            with patch(
                "apps.test_scenario.utils.download_and_upload_image.default_storage"
            ) as mock_storage:
                mock_storage.save.return_value = "uuid/photo.jpg"
                download_and_upload_image("https://example.com/path/photo.jpg")

        args = mock_storage.save.call_args[0]
        dest_key = args[0]
        self.assertTrue(dest_key.endswith("photo.jpg"))

    def test_generates_filename_from_content_type_when_url_has_no_extension(self):
        """Should generate filename using content-type when URL path has no extension."""
        with patch(
            "apps.test_scenario.utils.download_and_upload_image.requests.get",
            return_value=self._make_response(content_type="image/png"),
        ):
            with patch(
                "apps.test_scenario.utils.download_and_upload_image.default_storage"
            ) as mock_storage:
                mock_storage.save.return_value = "uuid/image_20250101_000000.png"
                download_and_upload_image("https://example.com/no-extension")

        args = mock_storage.save.call_args[0]
        dest_key = args[0]
        self.assertTrue(dest_key.endswith(".png"))

    def test_strips_query_params_when_extracting_filename(self):
        """Should strip query parameters from the URL before extracting the filename."""
        with patch(
            "apps.test_scenario.utils.download_and_upload_image.requests.get",
            return_value=self._make_response(),
        ):
            with patch(
                "apps.test_scenario.utils.download_and_upload_image.default_storage"
            ) as mock_storage:
                mock_storage.save.return_value = "uuid/photo.jpg"
                download_and_upload_image(
                    "https://example.com/photo.jpg?X-Amz-Signature=abc"
                )

        args = mock_storage.save.call_args[0]
        dest_key = args[0]
        self.assertTrue(dest_key.endswith("photo.jpg"))

    # ==================== Error propagation ====================

    def test_raises_on_http_error(self):
        """Should propagate HTTPError when the download request fails."""
        from requests import HTTPError
        with patch(
            "apps.test_scenario.utils.download_and_upload_image.requests.get",
            return_value=self._make_response(status=404),
        ):
            with self.assertRaises(HTTPError):
                download_and_upload_image("https://example.com/missing.jpg")
