"""
Gemini Image Generation Service.

Provides a clean interface to Gemini's image generation capabilities.
Used for generating identity images from reference photos and prompts.
"""

import os
from typing import List, Optional, Tuple
from PIL import Image
from google import genai
from google.genai import types
from google.genai.chats import Chat
from google.genai.types import Content, GenerateContentConfig, GenerateContentResponse

from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


class GeminiImageService:
    """
    Service for generating images using Google's Gemini API.

    This is a "dumb" service that just handles the API call.
    Prompt construction is handled by PromptManager.
    """

    # Gemini model for image generation
    MODEL = "gemini-3-pro-image-preview"

    # Default image configuration
    DEFAULT_ASPECT_RATIO = "16:9"
    DEFAULT_RESOLUTION = "4K"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini client.

        Args:
            api_key: Optional API key. If not provided, reads from GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is required. Set it in .env or pass to constructor."
            )

        self.client = genai.Client(api_key=self.api_key)
        log.info("GeminiImageService initialized")

    def generate_image(
        self,
        prompt: str,
        reference_images: List[Image.Image],
        aspect_ratio: str = DEFAULT_ASPECT_RATIO,
        resolution: str = DEFAULT_RESOLUTION,
    ) -> Optional[Image.Image]:
        """
        Generate an image using Gemini from a prompt and reference images.

        Args:
            prompt: The text prompt describing what to generate
            reference_images: List of PIL Images to use as reference
            aspect_ratio: Output aspect ratio (default: "16:9")
                         Options: "1:1","2:3","3:2","3:4","4:3","4:5","5:4","9:16","16:9","21:9"
            resolution: Output resolution (default: "4K")
                       Options: "1K", "2K", "4K"

        Returns:
            Generated PIL Image, or None if generation failed
        """
        if not reference_images:
            log.warning("No reference images provided for image generation")

        log.info(
            f"Generating image with {len(reference_images)} reference images, "
            f"aspect_ratio={aspect_ratio}, resolution={resolution}"
        )
        log.debug(f"Prompt: {prompt[:200]}...")

        # Build content list: prompt followed by reference images
        contents = [prompt] + reference_images

        try:
            response = self.client.models.generate_content(
                model=self.MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio,
                        image_size=resolution,
                    ),
                ),
            )

            # Extract image from response
            for part in response.parts:
                if part.inline_data is not None:
                    image = part.as_image()
                    log.info("Image generated successfully")
                    return image
                if part.text is not None:
                    log.debug(f"Gemini response text: {part.text}")

            log.warning("No image found in Gemini response")
            return None

        except Exception as e:
            log.error(f"Gemini image generation failed: {str(e)}", exc_info=True)
            raise

    def generate_image_bytes(
        self,
        prompt: str,
        reference_images: List[Image.Image],
        aspect_ratio: str = DEFAULT_ASPECT_RATIO,
        resolution: str = DEFAULT_RESOLUTION,
        format: str = "PNG",
    ) -> Optional[bytes]:
        """
        Generate an image and return it as bytes.

        Convenience method for when you need bytes instead of a PIL Image.

        Args:
            prompt: The text prompt describing what to generate
            reference_images: List of PIL Images to use as reference
            aspect_ratio: Output aspect ratio (default: "16:9")
            resolution: Output resolution (default: "4K")
            format: Image format for output (default: "PNG")

        Returns:
            Image bytes, or None if generation failed
        """
        import io

        image = self.generate_image(
            prompt=prompt,
            reference_images=reference_images,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
        )

        if image is None:
            return None

        buffer = io.BytesIO()
        image.save(buffer, format=format)
        buffer.seek(0)
        return buffer.getvalue()

    def create_chat(
        self,
        history: Optional[List[Content]] = None,
        config: Optional[GenerateContentConfig] = None,
    ) -> Chat:
        """
        Create a new Gemini chat session for image generation.

        Args:
            history: Optional existing history to restore a session
            config: Optional config override

        Returns:
            Gemini Chat object
        """
        default_config = GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio="16:9",
                image_size="4K",
            ),
        )

        return self.client.chats.create(
            model=self.MODEL,
            config=config or default_config,
            history=history or [],
        )

    def send_chat_message(
        self,
        chat: Chat,
        message: str,
        images: Optional[List[Image.Image]] = None,
    ) -> Tuple[Optional[Image.Image], GenerateContentResponse]:
        """
        Send a message to a chat session and extract the generated image.

        Args:
            chat: The Gemini chat session
            message: Text message/prompt to send
            images: Optional PIL images to include with the message

        Returns:
            Tuple of (generated PIL Image or None, full response)
        """
        # Build content: text + optional images
        contents = [message]
        if images:
            contents.extend(images)

        log.info(f"Sending chat message with {len(images) if images else 0} images")
        log.debug(f"Message: {message[:200]}...")

        response = chat.send_message(contents)

        # Extract image from response. Use the *last* image part so that in
        # multi-turn edits we return the newly generated image, not an earlier
        # part (e.g. reference echo or thinking image). See research scripts
        # that skip thought parts and take the final image.
        generated_image = None
        for part in response.parts:
            if getattr(part, "thought", False):
                continue
            if part.text is not None:
                log.debug(f"Chat response text: {part.text[:200]}...")
            if part.inline_data is not None:
                generated_image = part.as_image()
        if generated_image is not None:
            log.info("Image generated successfully from chat")

        return generated_image, response

