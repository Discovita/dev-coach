"""
Tests for extract_s3_key_from_url utility.
"""

from unittest.mock import patch

from django.test import TestCase

from apps.test_scenario.utils import extract_s3_key_from_url


class TestExtractS3KeyFromUrl(TestCase):
    """extract_s3_key_from_url tests."""

    # ==================== None / empty input ====================

    def test_returns_none_for_none_input(self):
        """Should return None when URL is None."""
        self.assertIsNone(extract_s3_key_from_url(None))

    def test_returns_none_for_empty_string(self):
        """Should return None when URL is an empty string."""
        self.assertIsNone(extract_s3_key_from_url(""))

    # ==================== /media/ path ====================

    def test_extracts_key_from_media_url(self):
        """Should extract key from a URL containing /media/."""
        url = "https://example.s3.amazonaws.com/media/uuid-123/photo.jpg"
        result = extract_s3_key_from_url(url)
        self.assertEqual(result, "uuid-123/photo.jpg")

    def test_strips_query_params_from_media_url(self):
        """Should strip query string from URLs with /media/ path."""
        url = "https://example.s3.amazonaws.com/media/uuid-123/photo.jpg?X-Amz-Signature=abc"
        result = extract_s3_key_from_url(url)
        self.assertEqual(result, "uuid-123/photo.jpg")

    def test_url_decodes_key_from_media_url(self):
        """Should URL-decode percent-encoded characters in the key."""
        url = "https://example.s3.amazonaws.com/media/folder%20with%20spaces/photo.jpg"
        result = extract_s3_key_from_url(url)
        self.assertEqual(result, "folder with spaces/photo.jpg")

    # ==================== Bucket domain ====================

    def test_extracts_key_from_bucket_domain_url(self):
        """Should extract key from a standard S3 bucket URL."""
        url = "https://my-bucket.s3.amazonaws.com/some/key/photo.jpg"
        with patch("apps.test_scenario.utils.extract_s3_key.settings") as mock_settings:
            mock_settings.STORAGES = {
                "default": {"OPTIONS": {"bucket_name": "my-bucket", "custom_domain": None}}
            }
            result = extract_s3_key_from_url(url)
        self.assertEqual(result, "some/key/photo.jpg")

    # ==================== Custom domain ====================

    def test_extracts_key_from_custom_domain_url(self):
        """Should extract key from a custom-domain S3 URL."""
        url = "https://cdn.example.com/uuid-abc/photo.jpg"
        with patch("apps.test_scenario.utils.extract_s3_key.settings") as mock_settings:
            mock_settings.STORAGES = {
                "default": {
                    "OPTIONS": {
                        "bucket_name": "my-bucket",
                        "custom_domain": "cdn.example.com",
                    }
                }
            }
            result = extract_s3_key_from_url(url)
        self.assertEqual(result, "uuid-abc/photo.jpg")

    # ==================== Unrecognised URL ====================

    def test_returns_none_for_unrecognised_url(self):
        """Should return None for a URL that matches no known pattern."""
        url = "https://totally-unrelated-domain.com/some/path.jpg"
        result = extract_s3_key_from_url(url)
        self.assertIsNone(result)
