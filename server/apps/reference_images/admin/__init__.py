"""
Django admin configuration for the reference_images app.

Exports:
    ReferenceImageAdmin: Standalone admin for ReferenceImage.
    ReferenceImageInline: TabularInline for embedding in the User admin.
"""

from apps.reference_images.admin.reference_image_admin import ReferenceImageAdmin
from apps.reference_images.admin.reference_image_inline import ReferenceImageInline

__all__ = [
    "ReferenceImageAdmin",
    "ReferenceImageInline",
]
