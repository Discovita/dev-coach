"""
Utility to load PIL Image objects from ReferenceImage models.
"""
from PIL import Image as PILImage
from typing import List
from io import BytesIO

from apps.reference_images.models import ReferenceImage
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")

# Maximum dimension for reference images (to avoid Gemini API limits)
MAX_IMAGE_DIMENSION = 1024


def _resize_if_needed(image: PILImage.Image, max_dim: int = MAX_IMAGE_DIMENSION) -> PILImage.Image:
    """
    Resize image if either dimension exceeds max_dim, preserving aspect ratio.
    """
    width, height = image.size
    if width <= max_dim and height <= max_dim:
        return image
    
    # Calculate new size preserving aspect ratio
    if width > height:
        new_width = max_dim
        new_height = int(height * (max_dim / width))
    else:
        new_height = max_dim
        new_width = int(width * (max_dim / height))
    
    log.info(f"Resizing image from {width}x{height} to {new_width}x{new_height}")
    return image.resize((new_width, new_height), PILImage.Resampling.LANCZOS)


def load_pil_images_from_references(reference_images: List[ReferenceImage]) -> List[PILImage.Image]:
    """
    Load PIL Image objects from ReferenceImage models.
    
    Args:
        reference_images: List of ReferenceImage model instances
        
    Returns:
        List of PIL Image objects (skips any that fail to load)
    """
    log.info(f"Starting to load {len(reference_images)} reference images from S3")
    pil_images = []
    
    for idx, ref_image in enumerate(reference_images):
        log.debug(f"Processing reference image {idx + 1}/{len(reference_images)}: {ref_image.id}")
        
        if not ref_image.image:
            log.warning(f"ReferenceImage {ref_image.id} has no image file")
            continue
            
        try:
            # Read from S3/storage backend
            log.debug(f"Opening image from S3: {ref_image.image.name}")
            ref_image.image.open()
            log.debug(f"Reading image data...")
            image_data = ref_image.image.read()
            log.debug(f"Read {len(image_data)} bytes, closing file")
            ref_image.image.close()
            
            # Convert to PIL Image
            log.debug(f"Converting to PIL Image...")
            pil_image = PILImage.open(BytesIO(image_data))
            
            # Resize if too large (to avoid Gemini API limits)
            pil_image = _resize_if_needed(pil_image)
            
            pil_images.append(pil_image)
            log.info(f"Successfully loaded reference image {idx + 1}/{len(reference_images)} ({pil_image.size[0]}x{pil_image.size[1]})")
            
        except Exception as e:
            log.error(f"Failed to load ReferenceImage {ref_image.id}: {e}", exc_info=True)
            continue
    
    log.info(f"Finished loading reference images: {len(pil_images)} successful out of {len(reference_images)}")
    return pil_images

