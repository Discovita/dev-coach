from typing import Set
from apps.reference_images.models import ReferenceImage
from apps.users.models import User

MAX_REFERENCE_IMAGES = 5


def get_next_available_order(user: User) -> int:
    """
    Get the next available order slot for a user's reference images.

    Args:
        user: The user to check for available slots

    Returns:
        The next available order number (0-4)

    Raises:
        ValueError: If all 5 slots are filled
    """
    existing_orders: Set[int] = set(
        ReferenceImage.objects.filter(user=user).values_list("order", flat=True)
    )

    for i in range(MAX_REFERENCE_IMAGES):
        if i not in existing_orders:
            return i

    raise ValueError(f"Maximum {MAX_REFERENCE_IMAGES} reference images allowed")

