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
        reference_image: The ReferenceImage instance to update
        image_file: The new image file to upload

    Returns:
        The updated ReferenceImage instance

    Raises:
        ValidationError: If no image file provided
    """
    if not image_file:
        raise ValidationError("No image file provided")

    # Delete old image if exists
    if reference_image.image:
        reference_image.image.delete()

    reference_image.image = image_file
    reference_image.save()

    return reference_image

