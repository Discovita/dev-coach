"""
download_and_upload_image

Download an image from an external URL and upload it via Django's default storage.
"""

import os
from datetime import datetime

import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from apps.test_scenario.utils.build_image_dest_key import build_image_dest_key
from services.logger import configure_logging

log = configure_logging(__name__)


def download_and_upload_image(
    image_url: str,
    upload_to_path: str | None = None,
) -> str | None:
    """
    Download an image from an external URL and save it via default_storage.

    Args:
        image_url: The public URL of the image to download.
        upload_to_path: Optional destination directory in storage.

    Returns:
        The saved storage key, or ``None`` on failure.

    Raises:
        requests.HTTPError: If the download request returns a non-2xx status.
    """
    response = requests.get(image_url, timeout=30)
    response.raise_for_status()

    filename = os.path.basename(image_url.split("?")[0])
    if not filename or "." not in filename:
        content_type = response.headers.get("content-type", "image/jpeg")
        ext = content_type.split("/")[-1] if "/" in content_type else "jpg"
        filename = f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"

    dest_key = build_image_dest_key(filename, upload_to_path, include_media_prefix=False)
    return default_storage.save(dest_key, ContentFile(response.content))
