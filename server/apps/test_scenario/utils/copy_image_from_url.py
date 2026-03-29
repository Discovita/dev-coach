"""
Copy an image from a URL (S3 or external) to a new S3 location.

See: apps/test_scenario/utils/__init__.py
"""

import os
import uuid
from datetime import datetime

import boto3

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

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
            return _copy_within_s3(bucket_name, source_key, upload_to_path)
        else:
            return _download_and_upload(image_url, upload_to_path)

    except Exception as e:
        log.error(f"Error copying image from URL {image_url}: {e}", exc_info=True)
        return None


def _copy_within_s3(
    bucket_name: str, source_key: str, upload_to_path: str | None
) -> str | None:
    """Server-side S3 copy, probing multiple key variants."""
    region_name = None
    if hasattr(settings, "STORAGES") and "default" in settings.STORAGES:
        region_name = settings.STORAGES["default"]["OPTIONS"].get("region_name")
    if not region_name:
        region_name = getattr(settings, "AWS_REGION", "us-east-1")

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=region_name,
    )

    # Probe several key variants (with/without media/ prefix)
    possible_keys = list(dict.fromkeys([source_key, f"media/{source_key}"]))
    actual_key = None
    for candidate in possible_keys:
        try:
            s3_client.head_object(Bucket=bucket_name, Key=candidate)
            actual_key = candidate
            break
        except s3_client.exceptions.ClientError as e:
            if e.response["Error"]["Code"] != "404":
                raise

    if not actual_key:
        log.error(f"Image not found in S3 with keys: {possible_keys}")
        return None

    filename = os.path.basename(actual_key)
    dest_key = _build_dest_key(filename, upload_to_path, include_media_prefix=True)

    s3_client.copy_object(
        CopySource={"Bucket": bucket_name, "Key": actual_key},
        Bucket=bucket_name,
        Key=dest_key,
    )
    return dest_key


def _download_and_upload(image_url: str, upload_to_path: str | None) -> str | None:
    """Download from an external URL and save via default_storage."""
    import requests

    response = requests.get(image_url, timeout=30)
    response.raise_for_status()

    filename = os.path.basename(image_url.split("?")[0])
    if not filename or "." not in filename:
        content_type = response.headers.get("content-type", "image/jpeg")
        ext = content_type.split("/")[-1] if "/" in content_type else "jpg"
        filename = f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"

    dest_key = _build_dest_key(filename, upload_to_path, include_media_prefix=False)
    return default_storage.save(dest_key, ContentFile(response.content))


def _build_dest_key(
    filename: str, upload_to_path: str | None, *, include_media_prefix: bool
) -> str:
    """Build a UUID-based destination key."""
    if upload_to_path:
        now = datetime.now()
        dest_path = (
            now.strftime(upload_to_path) if "%Y" in upload_to_path else upload_to_path
        )
        return os.path.join(dest_path, filename).replace("\\", "/")

    uuid_dir = str(uuid.uuid4())
    if include_media_prefix:
        return os.path.join("media", uuid_dir, filename).replace("\\", "/")
    return os.path.join(uuid_dir, filename).replace("\\", "/")
