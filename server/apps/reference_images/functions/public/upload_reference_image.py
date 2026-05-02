"""
Upload or replace the image file for a reference image.

See: apps/reference_images/functions/public/__init__.py
"""

from typing import Any

from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.reference_images.models import ReferenceImage


@transaction.atomic
def upload_reference_image(
    reference_image: ReferenceImage,
    image_file: Any,
) -> ReferenceImage:
    """
    Upload or replace the image file for a reference image.

    Args:
        reference_image: The ReferenceImage instance to update.
        image_file: The new image file to upload.

    Returns:
        The updated ReferenceImage instance.

    Raises:
        ValidationError: If no image file provided.
    """
    if not image_file:
        raise ValidationError("No image file provided")

    if reference_image.image:
        try:
            reference_image.image.delete()
        except Exception:
            pass  # Best-effort cleanup; proceed with the new upload

    reference_image.image = image_file
    reference_image.save()
    return reference_image
