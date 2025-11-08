from django.db import models
from versatileimagefield.fields import VersatileImageField, PPOIField
from uuid_upload_path import upload_to


class ImageMixin(models.Model):
    """
    An abstract base class model that provides a VersatileImageField Image with PPOI
    """

    image = VersatileImageField(
        "Image",
        upload_to=upload_to,
        ppoi_field="image_ppoi",
        # placeholder_image=OnStoragePlaceholderImage(path='path/to/placeholder-image.jpg'),
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