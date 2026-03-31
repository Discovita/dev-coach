"""
TabularInline for embedding reference images in the User admin.

See: apps/reference_images/admin/__init__.py
"""

from django.contrib import admin

from apps.reference_images.admin.image_preview import render_image_preview
from apps.reference_images.models import ReferenceImage


class ReferenceImageInline(admin.TabularInline):
    """
    Inline admin for ReferenceImage, shown when viewing/editing a User.
    """

    model = ReferenceImage
    extra = 0
    readonly_fields = ("id", "order", "image_preview", "created_at", "updated_at")
    fields = ("order", "name", "image_preview", "image", "created_at", "updated_at")
    can_delete = True
    verbose_name = "Reference Image"
    verbose_name_plural = "Reference Images"
    max_num = 5

    def image_preview(self, obj):
        return render_image_preview(obj, max_size=100)

    image_preview.short_description = "Preview"
