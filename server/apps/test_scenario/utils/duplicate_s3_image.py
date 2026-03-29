"""
Duplicate an existing S3 image to a new UUID-based key via server-side copy.

See: apps/test_scenario/utils/__init__.py
"""

import os
import uuid

import boto3

from django.conf import settings

from services.logger import configure_logging

log = configure_logging(__name__)


def duplicate_s3_image(
    source_image_field, new_upload_to_path: str | None = None
) -> str | None:
    """
    Copy an S3 object to a new key within the same bucket.

    Args:
        source_image_field: A Django ``VersatileImageField`` instance whose
            ``.name`` attribute holds the current S3 key.
        new_upload_to_path: Optional destination directory. Falls back to a
            UUID-based path under ``media/``.

    Returns:
        The destination S3 key, or ``None`` on failure.
    """
    if not source_image_field or not source_image_field.name:
        return None

    try:
        bucket_name = None
        region_name = None
        if hasattr(settings, "STORAGES") and "default" in settings.STORAGES:
            bucket_name = settings.STORAGES["default"]["OPTIONS"].get("bucket_name")
            region_name = settings.STORAGES["default"]["OPTIONS"].get(
                "region_name", "us-east-1"
            )

        if not bucket_name:
            log.error("Could not determine bucket name from STORAGES settings")
            return None

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=region_name,
        )
        source_key = source_image_field.name
        filename = os.path.basename(source_key)

        if new_upload_to_path:
            dest_key = os.path.join(new_upload_to_path, filename).replace("\\", "/")
        else:
            dest_key = os.path.join("media", str(uuid.uuid4()), filename).replace(
                "\\", "/"
            )

        s3_client.copy_object(
            CopySource={"Bucket": bucket_name, "Key": source_key},
            Bucket=bucket_name,
            Key=dest_key,
        )
        return dest_key

    except Exception as e:
        log.error(f"Error duplicating S3 image: {e}", exc_info=True)
        return None
