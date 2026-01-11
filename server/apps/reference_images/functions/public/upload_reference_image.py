from typing import Any
from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.reference_images.models import ReferenceImage
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


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
    log.info(f"upload_reference_image called for ReferenceImage {reference_image.id}")
    
    try:
        if not image_file:
            log.warning(f"No image file provided for ReferenceImage {reference_image.id}")
            raise ValidationError("No image file provided")

        # Delete old image if exists
        if reference_image.image:
            log.info(f"Deleting old image for ReferenceImage {reference_image.id}")
            try:
                reference_image.image.delete()
                log.info(f"Successfully deleted old image for ReferenceImage {reference_image.id}")
            except Exception as e:
                log.warning(f"Error deleting old image (continuing anyway): {e}")

        log.info(f"Assigning new image file to ReferenceImage {reference_image.id}")
        reference_image.image = image_file
        log.info(f"Saving ReferenceImage {reference_image.id} with new image")
        reference_image.save()
        log.info(f"Successfully uploaded image for ReferenceImage {reference_image.id}")

        return reference_image
    except ValidationError:
        raise
    except Exception as e:
        log.error(f"Unexpected error in upload_reference_image: {e}", exc_info=True)
        raise

