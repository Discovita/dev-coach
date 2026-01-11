from django.db import transaction
from apps.reference_images.models import ReferenceImage


@transaction.atomic
def delete_reference_image(reference_image: ReferenceImage) -> None:
    """
    Delete a reference image and its associated file.

    Args:
        reference_image: The ReferenceImage instance to delete
    """
    # Delete the image file if it exists
    if reference_image.image:
        reference_image.image.delete()

    reference_image.delete()

