"""
copy_image_from_url

Copy an image from a URL (S3 or external) to a new S3 location.

See: apps/test_scenario/utils/__init__.py
"""

from django.conf import settings

from apps.test_scenario.utils.copy_image_within_s3 import copy_image_within_s3
from apps.test_scenario.utils.download_and_upload_image import download_and_upload_image
from apps.test_scenario.utils.extract_s3_key import extract_s3_key_from_url
from services.logger import configure_logging

log = configure_logging(__name__)


def copy_image_from_url(
    image_url: str, upload_to_path: str | None = None
) -> str | None:
    """
    Copy an image from *image_url* into S3.

    If the URL points to an object in the same bucket, a server-side S3 copy
    is used (no download).  Otherwise the image is fetched over HTTP and
    uploaded via ``default_storage``.

    Args:
        image_url: Source URL (S3 or external).
        upload_to_path: Optional destination directory.  Falls back to a
            UUID-based path.

    Returns:
        The S3 key for the new copy, or ``None`` on failure.
    """
    if not image_url:
        return None

    try:
        bucket_name = None
        s3_custom_domain = None
        if hasattr(settings, "STORAGES") and "default" in settings.STORAGES:
            bucket_name = settings.STORAGES["default"]["OPTIONS"].get("bucket_name")
            s3_custom_domain = settings.STORAGES["default"]["OPTIONS"].get(
                "custom_domain"
            )

        if not bucket_name:
            log.error("Could not determine bucket name from STORAGES settings")
            return None

        s3_domain = f"{bucket_name}.s3.amazonaws.com"
        is_s3_url = s3_domain in image_url or (
            s3_custom_domain and s3_custom_domain in image_url
        )
        source_key = extract_s3_key_from_url(image_url) if is_s3_url else None

        if is_s3_url and source_key:
            return copy_image_within_s3(bucket_name, source_key, upload_to_path)
        else:
            return download_and_upload_image(image_url, upload_to_path)

    except Exception as e:
        log.error(f"Error copying image from URL {image_url}: {e}", exc_info=True)
        return None
