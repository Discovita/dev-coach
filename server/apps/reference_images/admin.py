"""
Admin configuration for Reference Images.
Provides inline admin for viewing reference images when editing a User.
"""

from django.contrib import admin
from django.utils.html import format_html
from apps.reference_images.models import ReferenceImage


class ReferenceImageInline(admin.TabularInline):
    """
    Inline admin for ReferenceImage model.
    Shows reference images when viewing/editing a User in the admin panel.
    """
    model = ReferenceImage
    extra = 0
    readonly_fields = ("id", "order", "image_preview", "created_at", "updated_at")
    fields = ("order", "name", "image_preview", "image", "created_at", "updated_at")
    can_delete = True
    verbose_name = "Reference Image"
    verbose_name_plural = "Reference Images"
    max_num = 5  # Maximum 5 reference images per user

    def image_preview(self, obj):
        """Display a thumbnail preview of the image."""
        if obj.image:
            try:
                # Try to get thumbnail URL
                thumbnail_url = obj.image.thumbnail["100x100"].url
                return format_html(
                    '<img src="{}" style="max-width: 100px; max-height: 100px; object-fit: contain;" />',
                    thumbnail_url
                )
            except Exception:
                # Fallback to original URL if thumbnail generation fails
                try:
                    original_url = obj.image.url
                    return format_html(
                        '<img src="{}" style="max-width: 100px; max-height: 100px; object-fit: contain;" />',
                        original_url
                    )
                except Exception:
                    return "Image unavailable"
        return "No image"
    
    image_preview.short_description = "Preview"


@admin.register(ReferenceImage)
class ReferenceImageAdmin(admin.ModelAdmin):
    """
    Standalone admin for ReferenceImage model.
    Allows direct management of reference images.
    """
    list_display = ("id", "user", "name", "order", "image_preview", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at", "order")
    search_fields = ("user__email", "user__first_name", "user__last_name", "name")
    readonly_fields = ("id", "image_preview", "created_at", "updated_at")
    fields = ("id", "user", "name", "order", "image", "image_preview", "created_at", "updated_at")
    raw_id_fields = ("user",)

    def image_preview(self, obj):
        """Display a thumbnail preview of the image."""
        if obj.image:
            try:
                # Try to get thumbnail URL
                thumbnail_url = obj.image.thumbnail["100x100"].url
                return format_html(
                    '<img src="{}" style="max-width: 200px; max-height: 200px; object-fit: contain;" />',
                    thumbnail_url
                )
            except Exception:
                # Fallback to original URL if thumbnail generation fails
                try:
                    original_url = obj.image.url
                    return format_html(
                        '<img src="{}" style="max-width: 200px; max-height: 200px; object-fit: contain;" />',
                        original_url
                    )
                except Exception:
                    return "Image unavailable"
        return "No image"
    
    image_preview.short_description = "Preview"
