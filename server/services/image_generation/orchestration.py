"""
Identity Image Generation Orchestration.

This module provides the high-level orchestration function that combines:
- PromptManager (for building the prompt from identity context)
- GeminiImageService (for generating the image)
- Reference image loading utilities

Used by:
- AdminIdentityViewSet.generate_image (admin endpoints)
- Future: Coach action handler for image generation
"""
from PIL import Image as PILImage
from typing import List, Optional

from apps.identities.models import Identity
from apps.reference_images.models import ReferenceImage
from services.image_generation.gemini_image_service import GeminiImageService
from services.image_generation.utils.load_pil_images import load_pil_images_from_references
from services.prompt_manager.manager import PromptManager
from services.logger import configure_logging

log = configure_logging(__name__)


def generate_identity_image(
    identity: Identity,
    reference_images: List[ReferenceImage],
    additional_prompt: str = "",
    aspect_ratio: str = "16:9",
    resolution: str = "4K",
) -> Optional[PILImage.Image]:
    """
    Generate an identity image using Gemini.
    
    This is the main orchestration function that:
    1. Builds the prompt using PromptManager
    2. Loads PIL images from ReferenceImage models
    3. Calls GeminiImageService to generate the image
    
    Args:
        identity: The Identity to generate an image for
        reference_images: List of ReferenceImage models for the user
        additional_prompt: Optional extra instructions from admin
        aspect_ratio: Image aspect ratio (default "16:9")
        resolution: Image resolution (default "4K")
        
    Returns:
        PIL Image object, or None if generation failed
        
    Note:
        This function is used by both admin endpoints and future Coach actions.
        The caller is responsible for saving the image to S3 if needed.
    """
    log.info(f"Generating image for identity: {identity.name}")
    
    # 1. Build prompt using PromptManager
    prompt_manager = PromptManager()
    prompt = prompt_manager.create_image_generation_prompt(identity, additional_prompt)
    log.debug(f"Built prompt: {prompt[:100]}...")
    
    # 2. Load PIL images from ReferenceImage models
    pil_images = load_pil_images_from_references(reference_images)
    log.info(f"Loaded {len(pil_images)} reference images")
    
    if not pil_images:
        log.warning("No reference images could be loaded")
        return None
    
    # 3. Generate image using Gemini
    service = GeminiImageService()
    image = service.generate_image(
        prompt=prompt,
        reference_images=pil_images,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
    )
    
    if image:
        log.info(f"Successfully generated image for identity: {identity.name}")
    else:
        log.warning(f"Image generation returned None for identity: {identity.name}")
    
    return image

