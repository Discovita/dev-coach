from typing import Any, Optional
from uuid import UUID
from django.db import transaction
from rest_framework.exceptions import NotFound
from apps.reference_images.models import ReferenceImage
from apps.reference_images.functions.public import create_reference_image
from apps.users.models import User


@transaction.atomic
def create_reference_image_for_user(
    user_id: UUID,
    name: str = "",
    order: Optional[int] = None,
    image_file: Optional[Any] = None,
) -> ReferenceImage:
    """
    Admin function to create a reference image for any user by ID.

    Args:
        user_id: UUID of the target user
        name: Optional name/label for the image
        order: Optional specific order slot (0-4)
        image_file: Optional image file to upload immediately

    Returns:
        The created ReferenceImage instance

    Raises:
        NotFound: If user does not exist
        ValidationError: If user has reached maximum images
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise NotFound(f"User {user_id} not found")

    return create_reference_image(
        user=user,
        name=name,
        order=order,
        image_file=image_file,
    )

