"""
Identity Image Generation Orchestration.

This module provides high-level orchestration functions for:
- Starting new image generation chat sessions
- Continuing existing chat sessions with edit prompts

Used by:
- AdminIdentityViewSet (admin endpoints)
- IdentityImageChatViewSet (user endpoints)
"""
from PIL import Image as PILImage
from typing import List, Optional, Tuple

from apps.identities.models import Identity, IdentityImageChat
from apps.reference_images.models import ReferenceImage
from apps.users.models import User
from services.image_generation.gemini_image_service import GeminiImageService
from services.image_generation.utils import (
    load_pil_images_from_references,
    serialize_chat_history,
    deserialize_chat_history,
)
from services.prompt_manager.manager import PromptManager
from services.logger import configure_logging

log = configure_logging(__name__)


def generate_identity_image(
    identity: Identity,
    reference_images: List[ReferenceImage],
    user: User,
    additional_prompt: str = "",
    aspect_ratio: str = "16:9",
    resolution: str = "4K",
) -> Optional[PILImage.Image]:
    """
    Generate an identity image using Gemini.
    
    This is the main orchestration function that:
    1. Builds the prompt using PromptManager (with user appearance context)
    2. Loads PIL images from ReferenceImage models
    3. Calls GeminiImageService to generate the image
    
    Args:
        identity: The Identity to generate an image for
        reference_images: List of ReferenceImage models for the user
        user: The User for appearance preferences and context
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
    
    # 1. Build prompt using PromptManager (includes user appearance context)
    prompt_manager = PromptManager()
    prompt = prompt_manager.create_image_generation_prompt(
        identity=identity,
        user=user,
        additional_prompt=additional_prompt,
    )
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


def start_identity_image_chat(
    identity: Identity,
    reference_images: List[ReferenceImage],
    user: User,
    additional_prompt: str = "",
) -> Tuple[Optional[PILImage.Image], IdentityImageChat]:
    """
    Start a new image generation chat session.

    Creates a new Gemini chat, sends the initial prompt with reference images,
    stores the chat history in the database (replacing any existing chat),
    and returns the generated image.

    Args:
        identity: The Identity to generate an image for
        reference_images: List of ReferenceImage models for the user
        user: The User for appearance preferences and context
        additional_prompt: Optional extra instructions

    Returns:
        Tuple of (generated PIL Image or None, IdentityImageChat record)

    Raises:
        ValueError: If no reference images could be loaded
    """
    log.info(f"Starting new image chat for identity: {identity.name}, user: {user.id}")

    # 1. Build the initial prompt
    prompt_manager = PromptManager()
    prompt = prompt_manager.create_image_generation_prompt(
        identity=identity,
        user=user,
        additional_prompt=additional_prompt,
    )
    log.debug(f"Built prompt: {prompt[:100]}...")

    # 2. Load PIL images from references
    pil_images = load_pil_images_from_references(reference_images)
    log.info(f"Loaded {len(pil_images)} reference images")

    if not pil_images:
        raise ValueError("No reference images could be loaded")

    # 3. Create new Gemini chat and send initial message
    service = GeminiImageService()
    chat = service.create_chat()

    generated_image, response = service.send_chat_message(
        chat=chat,
        message=prompt,
        images=pil_images,
    )

    # 4. Serialize and store chat history
    history = chat.get_history(curated=True)
    serialized_history = serialize_chat_history(history)

    # 5. Create or replace the user's chat session
    chat_record, created = IdentityImageChat.objects.update_or_create(
        user=user,
        defaults={
            "identity": identity,
            "chat_history": serialized_history,
        },
    )

    action = "Created" if created else "Replaced"
    log.info(f"{action} chat session for user {user.id}, identity {identity.name}")

    return generated_image, chat_record


def continue_identity_image_chat(
    user: User,
    edit_prompt: str,
    reference_images: Optional[List[ReferenceImage]] = None,
) -> Tuple[Optional[PILImage.Image], IdentityImageChat]:
    """
    Continue an existing image chat with an edit request.

    Loads the existing chat history, restores the Gemini chat session,
    sends the edit prompt, updates the stored history, and returns the new image.

    Args:
        user: The User whose chat to continue
        edit_prompt: The edit instruction (e.g., "make the lighting warmer")
        reference_images: Optional reference images to include with the edit

    Returns:
        Tuple of (generated PIL Image or None, updated IdentityImageChat record)

    Raises:
        ValueError: If user has no active chat session
    """
    log.info(f"Continuing image chat for user: {user.id}")

    # 1. Load existing chat session
    try:
        chat_record = IdentityImageChat.objects.get(user=user)
    except IdentityImageChat.DoesNotExist:
        raise ValueError("No active image chat. Please start a new chat first.")

    if not chat_record.chat_history:
        raise ValueError("Chat history is empty. Please start a new chat first.")

    # 2. Deserialize history and restore chat
    history = deserialize_chat_history(chat_record.chat_history)

    service = GeminiImageService()
    chat = service.create_chat(history=history)

    # 3. Optionally load reference images
    pil_images = None
    if reference_images:
        pil_images = load_pil_images_from_references(reference_images)
        log.info(f"Including {len(pil_images)} reference images with edit")

    # 4. Send edit message
    generated_image, response = service.send_chat_message(
        chat=chat,
        message=edit_prompt,
        images=pil_images,
    )

    # 5. Update stored history
    updated_history = chat.get_history(curated=True)
    chat_record.chat_history = serialize_chat_history(updated_history)
    chat_record.save()

    log.info(f"Updated chat session for user {user.id}")

    return generated_image, chat_record

