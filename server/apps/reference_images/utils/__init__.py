"""
Utility helpers for the reference_images app.

Exports:
    get_next_available_order: Find the next open slot (0-4) for a user.
    MAX_REFERENCE_IMAGES: Maximum number of reference images per user.
"""

from apps.reference_images.utils.get_next_available_order import (
    MAX_REFERENCE_IMAGES,
    get_next_available_order,
)

__all__ = ["get_next_available_order", "MAX_REFERENCE_IMAGES"]
