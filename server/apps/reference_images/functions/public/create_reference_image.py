from typing import Any, Optional
from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.reference_images.models import ReferenceImage
from apps.reference_images.utils import get_next_available_order, MAX_REFERENCE_IMAGES
from apps.users.models import User


@transaction.atomic
def create_reference_image(
    user: User,
    name: str = "",
    order: Optional[int] = None,
    image_file: Optional[Any] = None,
) -> ReferenceImage:
    """
    Create a new reference image for a user.

    Args:
        user: The user to create the reference image for
        name: Optional name/label for the image
        order: Optional specific order slot (0-4). If not provided, uses next available.
        image_file: Optional image file to upload immediately

    Returns:
        The created ReferenceImage instance

    Raises:
        ValidationError: If user has reached maximum images or order is invalid
    """
    # Check limit
    existing_count = ReferenceImage.objects.filter(user=user).count()
    if existing_count >= MAX_REFERENCE_IMAGES:
        raise ValidationError(f"Maximum {MAX_REFERENCE_IMAGES} reference images allowed")

    # Determine order
    if order is None:
        order = get_next_available_order(user)
    elif order < 0 or order >= MAX_REFERENCE_IMAGES:
        raise ValidationError(f"Order must be between 0 and {MAX_REFERENCE_IMAGES - 1}")
    elif ReferenceImage.objects.filter(user=user, order=order).exists():
        raise ValidationError(f"Order {order} is already in use")

    # Create the reference image
    ref_image = ReferenceImage.objects.create(
        user=user,
        name=name,
        order=order,
    )

    # Upload image if provided
    if image_file:
        ref_image.image = image_file
        ref_image.save()

    return ref_image

