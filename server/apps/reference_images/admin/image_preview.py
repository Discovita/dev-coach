"""
Shared image preview helper for admin classes.

See: apps/reference_images/admin/__init__.py
"""

from django.utils.html import format_html


def render_image_preview(obj, max_size: int = 100) -> str:
    """
    Return an HTML img tag for a VersatileImageField, with thumbnail fallback.

    Args:
        obj: A model instance with an ``image`` VersatileImageField.
        max_size: Maximum width/height in pixels for the preview.

    Returns:
        An HTML string with an <img> tag, or a placeholder message.
    """
    if not obj.image:
        return "No image"

    style = f"max-width: {max_size}px; max-height: {max_size}px; object-fit: contain;"

    try:
        url = obj.image.thumbnail[f"{max_size}x{max_size}"].url
    except Exception:
        try:
            url = obj.image.url
        except Exception:
            return "Image unavailable"

    return format_html('<img src="{}" style="{}" />', url, style)
