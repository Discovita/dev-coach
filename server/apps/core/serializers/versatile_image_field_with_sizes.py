from versatileimagefield.serializers import VersatileImageFieldSerializer


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
                sizes = {
                    "original": instance.url,
                    "thumbnail": instance.thumbnail["100x100"].url,
                    "medium": instance.thumbnail["300x169"].url,  # 16:9 aspect ratio
                    "large": instance.thumbnail["600x338"].url,  # 16:9 aspect ratio
                }
                return sizes
            except Exception as e:
                return None
        else:
            return None
