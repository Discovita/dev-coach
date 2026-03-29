"""
Standalone admin for the ReferenceImage model.

See: apps/reference_images/admin/__init__.py
"""

from django.contrib import admin

from apps.reference_images.admin.image_preview import render_image_preview
from apps.reference_images.models import ReferenceImage


@admin.register(ReferenceImage)
class ReferenceImageAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for direct management of reference images.
    """

    list_display = (
        "id",
        "user",
        "name",
        "order",
        "image_preview",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at", "updated_at", "order")
    search_fields = ("user__email", "user__first_name", "user__last_name", "name")
    readonly_fields = ("id", "image_preview", "created_at", "updated_at")
    fields = (
        "id",
        "user",
        "name",
        "order",
        "image",
        "image_preview",
        "created_at",
        "updated_at",
    )
    raw_id_fields = ("user",)

    def image_preview(self, obj):
        return render_image_preview(obj, max_size=200)

    image_preview.short_description = "Preview"
