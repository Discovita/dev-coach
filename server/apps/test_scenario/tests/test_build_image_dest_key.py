"""
Tests for build_image_dest_key utility.
"""

import re
from unittest.mock import patch
from datetime import datetime

from django.test import TestCase

from apps.test_scenario.utils import build_image_dest_key


class TestBuildImageDestKey(TestCase):
    """build_image_dest_key tests."""

    # ==================== UUID-based (no path) ====================

    def test_returns_uuid_based_key_by_default(self):
        """Should return a UUID-directory key when no upload_to_path is given."""
        result = build_image_dest_key("photo.jpg")
        parts = result.split("/")
        self.assertEqual(len(parts), 2)
        self.assertEqual(parts[1], "photo.jpg")
        # UUID part should match UUID4 format
        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
        self.assertRegex(parts[0], uuid_pattern)

    def test_include_media_prefix_prepends_media(self):
        """Should prepend 'media/' when include_media_prefix=True."""
        result = build_image_dest_key("photo.jpg", include_media_prefix=True)
        self.assertTrue(result.startswith("media/"))
        parts = result.split("/")
        self.assertEqual(len(parts), 3)
        self.assertEqual(parts[0], "media")
        self.assertEqual(parts[2], "photo.jpg")

    def test_no_media_prefix_by_default(self):
        """Should not include media prefix by default."""
        result = build_image_dest_key("photo.jpg")
        self.assertFalse(result.startswith("media/"))

    # ==================== Custom upload_to_path ====================

    def test_uses_upload_to_path_when_provided(self):
        """Should use the provided upload_to_path directory."""
        result = build_image_dest_key("photo.jpg", upload_to_path="uploads/test")
        self.assertEqual(result, "uploads/test/photo.jpg")

    def test_strftime_formatting_in_upload_to_path(self):
        """Should apply strftime formatting when upload_to_path contains %Y."""
        fixed_dt = datetime(2025, 6, 15)
        with patch(
            "apps.test_scenario.utils.build_image_dest_key.datetime"
        ) as mock_dt:
            mock_dt.now.return_value = fixed_dt
            result = build_image_dest_key("photo.jpg", upload_to_path="uploads/%Y/%m")
        self.assertEqual(result, "uploads/2025/06/photo.jpg")

    def test_no_strftime_without_percent_Y(self):
        """Should use upload_to_path literally when it contains no strftime codes."""
        result = build_image_dest_key("photo.jpg", upload_to_path="static/images")
        self.assertEqual(result, "static/images/photo.jpg")

    # ==================== Path separator normalisation ====================

    def test_uses_forward_slashes(self):
        """Should use forward slashes, not backslashes."""
        result = build_image_dest_key("photo.jpg", upload_to_path="a/b/c")
        self.assertNotIn("\\", result)

    # ==================== Each call produces a unique key ====================

    def test_each_call_produces_unique_uuid_dir(self):
        """Should generate a different UUID directory on each call."""
        result1 = build_image_dest_key("photo.jpg")
        result2 = build_image_dest_key("photo.jpg")
        uuid1 = result1.split("/")[0]
        uuid2 = result2.split("/")[0]
        self.assertNotEqual(uuid1, uuid2)
