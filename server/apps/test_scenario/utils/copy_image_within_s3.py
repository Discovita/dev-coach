"""
copy_image_within_s3

Server-side copy of an S3 object to a new key within the same bucket.
"""

import os

import boto3
from django.conf import settings

from apps.test_scenario.utils.build_image_dest_key import build_image_dest_key
from services.logger import configure_logging

log = configure_logging(__name__)


def copy_image_within_s3(
    bucket_name: str,
    source_key: str,
    upload_to_path: str | None = None,
) -> str | None:
    """
    Perform a server-side S3 copy, probing multiple key variants.

    Tries the source key as-is, then prefixed with ``media/``, to handle
    cases where the stored key does or does not include the media prefix.

    Args:
        bucket_name: The S3 bucket name.
        source_key: The source object key (with or without ``media/`` prefix).
        upload_to_path: Optional destination directory for the copy.

    Returns:
        The destination S3 key, or ``None`` if the source object was not found.
    """
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
    dest_key = build_image_dest_key(filename, upload_to_path, include_media_prefix=True)
    s3_client.copy_object(
        CopySource={"Bucket": bucket_name, "Key": actual_key},
        Bucket=bucket_name,
        Key=dest_key,
    )
    return dest_key
