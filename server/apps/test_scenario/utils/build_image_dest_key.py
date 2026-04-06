"""
build_image_dest_key

Build a UUID-based destination S3 key for an image file.
"""

import os
import uuid
from datetime import datetime


def build_image_dest_key(
    filename: str,
    upload_to_path: str | None = None,
    *,
    include_media_prefix: bool = False,
) -> str:
    """
    Build a UUID-based destination key for an S3 image upload.

    Args:
        filename: The image filename (e.g. ``photo.jpg``).
        upload_to_path: Optional destination directory. Supports strftime
            format codes (e.g. ``uploads/%Y/%m``). If omitted, a UUID
            directory is generated.
        include_media_prefix: When ``True``, prepends ``media/`` to the
            generated UUID-based key. Has no effect when ``upload_to_path``
            is provided.

    Returns:
        The destination S3 key string.

    Example:
        >>> build_image_dest_key("photo.jpg", include_media_prefix=True)
        "media/<uuid>/photo.jpg"
    """
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
