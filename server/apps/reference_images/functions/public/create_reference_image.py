from typing import Any, Optional
from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.reference_images.models import ReferenceImage
from apps.reference_images.utils import get_next_available_order, MAX_REFERENCE_IMAGES
from apps.users.models import User
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


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
    log.info(f"create_reference_image called for user {user.id}, order={order}, has_image={bool(image_file)}")
    
    try:
        # Check limit
        log.debug(f"Checking image limit for user {user.id}")
        existing_count = ReferenceImage.objects.filter(user=user).count()
        log.debug(f"User {user.id} has {existing_count} existing reference images")
        if existing_count >= MAX_REFERENCE_IMAGES:
            log.warning(f"User {user.id} has reached maximum {MAX_REFERENCE_IMAGES} reference images")
            raise ValidationError(f"Maximum {MAX_REFERENCE_IMAGES} reference images allowed")

        # Determine order
        if order is None:
            log.debug(f"Order not specified, finding next available order for user {user.id}")
            order = get_next_available_order(user)
            log.info(f"Auto-assigned order {order} for user {user.id}")
        elif order < 0 or order >= MAX_REFERENCE_IMAGES:
            log.warning(f"Invalid order {order} for user {user.id}")
            raise ValidationError(f"Order must be between 0 and {MAX_REFERENCE_IMAGES - 1}")
        elif ReferenceImage.objects.filter(user=user, order=order).exists():
            log.warning(f"Order {order} already in use for user {user.id}")
            raise ValidationError(f"Order {order} is already in use")

        # Create the reference image
        log.info(f"Creating ReferenceImage for user {user.id} with order {order}")
        ref_image = ReferenceImage.objects.create(
            user=user,
            name=name,
            order=order,
        )
        log.info(f"Successfully created ReferenceImage {ref_image.id} for user {user.id}")

        # Upload image if provided
        if image_file:
            log.info(f"Uploading image file for ReferenceImage {ref_image.id}")
            ref_image.image = image_file
            ref_image.save()
            log.info(f"Successfully saved image file for ReferenceImage {ref_image.id}")

        log.info(f"create_reference_image completed successfully for ReferenceImage {ref_image.id}")
        return ref_image
    except ValidationError:
        raise
    except Exception as e:
        log.error(f"Unexpected error in create_reference_image: {e}", exc_info=True)
        raise

