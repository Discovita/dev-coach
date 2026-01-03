"""
Utility to load PIL Image objects from ReferenceImage models.
"""
from PIL import Image as PILImage
from typing import List
from io import BytesIO

from apps.reference_images.models import ReferenceImage
from services.logger import configure_logging

log = configure_logging(__name__)


def load_pil_images_from_references(reference_images: List[ReferenceImage]) -> List[PILImage.Image]:
    """
    Load PIL Image objects from ReferenceImage models.
    
    Args:
        reference_images: List of ReferenceImage model instances
        
    Returns:
        List of PIL Image objects (skips any that fail to load)
    """
    pil_images = []
    
    for ref_image in reference_images:
        if not ref_image.image:
            log.warning(f"ReferenceImage {ref_image.id} has no image file")
            continue
            
        try:
            # Read from S3/storage backend
            ref_image.image.open()
            image_data = ref_image.image.read()
            ref_image.image.close()
            
            # Convert to PIL Image
            pil_image = PILImage.open(BytesIO(image_data))
            pil_images.append(pil_image)
            
        except Exception as e:
            log.error(f"Failed to load ReferenceImage {ref_image.id}: {e}")
            continue
    
    return pil_images

