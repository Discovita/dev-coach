"""
ImageMixin — abstract base model providing a VersatileImageField with PPOI.

Used by:
- apps.identities.models.Identity
- apps.reference_images.models.ReferenceImage
"""

from uuid_upload_path import upload_to
from versatileimagefield.fields import PPOIField, VersatileImageField

from django.db import models


class ImageMixin(models.Model):
    """
    Abstract base model that provides a VersatileImageField image with
    Point-of-Interest (PPOI) support and automatic thumbnail generation.
    """

    image = VersatileImageField(
        "Image",
        upload_to=upload_to,
        ppoi_field="image_ppoi",
        null=True,
    )
    image_ppoi = PPOIField("Image PPOI")

    class Meta:
        abstract = True

    def create_image_sizes(self):
        if self.image:
            self.image.create_on_demand = True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.create_image_sizes()
