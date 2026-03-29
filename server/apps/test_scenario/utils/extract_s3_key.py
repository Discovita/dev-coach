"""
Shared helper for extracting S3 object keys from full URLs.

Used by process_identity_images and copy_image_from_url to avoid
duplicating the same URL-parsing logic across multiple modules.

See: apps/test_scenario/utils/__init__.py
"""

import urllib.parse

from django.conf import settings


def extract_s3_key_from_url(url: str) -> str | None:
    """
    Extract the S3 object key from a full URL.

    Handles three URL formats:
      - ``https://.../<bucket>.s3.amazonaws.com/<key>``
      - ``https://<custom_domain>/<key>``
      - ``https://.../<anything>/media/<key>``

    Query parameters are stripped and the key is URL-decoded.

    Returns:
        The decoded S3 key, or ``None`` if extraction fails.
    """
    if not url:
        return None

    bucket_name = None
    custom_domain = None
    if hasattr(settings, "STORAGES") and "default" in settings.STORAGES:
        bucket_name = settings.STORAGES["default"]["OPTIONS"].get("bucket_name")
        custom_domain = settings.STORAGES["default"]["OPTIONS"].get("custom_domain")

    key = None
    if "/media/" in url:
        key = url.split("/media/")[-1].split("?")[0]
    elif bucket_name and f"{bucket_name}.s3.amazonaws.com" in url:
        parts = url.split(f"{bucket_name}.s3.amazonaws.com/")
        if len(parts) > 1:
            key = parts[1].split("?")[0]
    elif custom_domain and custom_domain in url:
        parts = url.split(f"{custom_domain}/")
        if len(parts) > 1:
            key = parts[1].split("?")[0]

    if key:
        return urllib.parse.unquote(key)
    return None
