"""
delete_identity_image

Delete the existing S3 image for an identity template entry before replacing it.
"""

from django.core.files.storage import default_storage

from apps.test_scenario.utils.extract_s3_key import extract_s3_key_from_url
from services.logger import configure_logging

log = configure_logging(__name__)


def delete_identity_image(identity_data: dict) -> None:
    """
    Delete the S3 image referenced by an identity template entry.

    A no-op if the entry has no ``image`` key or the key cannot be extracted.

    Args:
        identity_data: A single identity dict from the template, which may
            contain an ``image`` key with an S3 URL.
    """
    old_url = identity_data.get("image")
    if not old_url:
        return
    key = extract_s3_key_from_url(old_url)
    if key:
        try:
            default_storage.delete(key)
        except Exception as e:
            log.warning(f"Failed to delete identity image: {e}")
