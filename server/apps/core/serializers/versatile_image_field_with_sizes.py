from versatileimagefield.serializers import VersatileImageFieldSerializer
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


class VersatileImageFieldWithSizes(VersatileImageFieldSerializer):
    def __init__(self, *args, **kwargs):
        # Provide default sizes if not specified (we override to_representation anyway)
        if 'sizes' not in kwargs:
            kwargs['sizes'] = [
                ('thumbnail', 'thumbnail__100x100'),
                ('medium', 'thumbnail__300x169'),
                ('large', 'thumbnail__600x338'),
            ]
        super().__init__(*args, **kwargs)
    
    def to_representation(self, instance):
        if instance:
            try:
                log.debug(f"Generating image URLs for instance: {instance}")
                log.debug(f"Getting original URL")
                original_url = instance.url
                log.debug(f"Original URL: {original_url}")
                
                log.debug(f"Getting thumbnail URL")
                thumbnail_url = instance.thumbnail["100x100"].url
                log.debug(f"Thumbnail URL: {thumbnail_url}")
                
                log.debug(f"Getting medium URL")
                medium_url = instance.thumbnail["300x169"].url
                log.debug(f"Medium URL: {medium_url}")
                
                log.debug(f"Getting large URL")
                large_url = instance.thumbnail["600x338"].url
                log.debug(f"Large URL: {large_url}")
                
                sizes = {
                    "original": original_url,
                    "thumbnail": thumbnail_url,
                    "medium": medium_url,
                    "large": large_url,
                }
                log.debug(f"Successfully generated all image URLs")
                return sizes
            except Exception as e:
                log.error(f"Error generating image URLs: {e}", exc_info=True)
                return None
        else:
            log.debug(f"No instance provided, returning None")
            return None
