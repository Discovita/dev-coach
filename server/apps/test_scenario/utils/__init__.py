"""
Utility functions for the test_scenario app.

Exports:
    validate_scenario_template: Validates a scenario template against the template serializers.
    process_identity_images: Handles image upload/deletion for identity images in templates.
    duplicate_s3_image: Copies an existing S3 image to a new UUID-based key.
    copy_image_from_url: Copies an image from a URL (S3 or external) to a new S3 location.
    extract_s3_key_from_url: Extracts the S3 object key from a full URL.
"""

from apps.test_scenario.utils.copy_image_from_url import copy_image_from_url
from apps.test_scenario.utils.duplicate_s3_image import duplicate_s3_image
from apps.test_scenario.utils.extract_s3_key import extract_s3_key_from_url
from apps.test_scenario.utils.process_identity_images import process_identity_images
from apps.test_scenario.utils.validate_scenario_template import (
    validate_scenario_template,
)

__all__ = [
    "validate_scenario_template",
    "process_identity_images",
    "duplicate_s3_image",
    "copy_image_from_url",
    "extract_s3_key_from_url",
]
