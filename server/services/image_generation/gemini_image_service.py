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


class ImageGenerationError(Exception):
    """
    Custom exception for image generation failures with detailed information.
    
    Attributes:
        message: Human-readable error message
        error_code: Machine-readable error code for frontend handling
        details: Additional details about the error
    """
    
    # Error codes for frontend handling
    BLOCKED_PROMPT = "BLOCKED_PROMPT"
    BLOCKED_RESPONSE = "BLOCKED_RESPONSE"
    EMPTY_RESPONSE = "EMPTY_RESPONSE"
    SAFETY_BLOCK = "SAFETY_BLOCK"
    RECITATION = "RECITATION"
    RATE_LIMITED = "RATE_LIMITED"
    MODEL_OVERLOADED = "MODEL_OVERLOADED"
    UNKNOWN = "UNKNOWN"
    
    def __init__(self, message: str, error_code: str = "UNKNOWN", details: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)
    
    def to_dict(self):
        return {
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
        }
    
    @classmethod
    def from_exception(cls, e: Exception) -> "ImageGenerationError":
        """
        Create an ImageGenerationError from a generic exception.
        Parses common error patterns to provide specific error codes.
        
        Args:
            e: The exception to convert
            
        Returns:
            ImageGenerationError with appropriate error code and message
        """
        error_str = str(e).lower()
        
        # Check for model overloaded (503 UNAVAILABLE)
        if "503" in str(e) or "unavailable" in error_str or "overloaded" in error_str:
            return cls(
                message="The AI model is currently overloaded. Please wait a moment and try again.",
                error_code=cls.MODEL_OVERLOADED,
                details=str(e),
            )
        
        # Check for rate limiting (429)
        if "429" in str(e) or "rate limit" in error_str or "quota" in error_str:
            return cls(
                message="Too many requests. Please wait a moment before trying again.",
                error_code=cls.RATE_LIMITED,
                details=str(e),
            )
        
        # Check for safety blocks
        if "safety" in error_str or "blocked" in error_str:
            return cls(
                message="Your request was blocked by safety filters. Please modify your prompt and try again.",
                error_code=cls.SAFETY_BLOCK,
                details=str(e),
            )
        
        # Default unknown error
        return cls(
            message=f"Image generation failed: {str(e)}",
            error_code=cls.UNKNOWN,
            details=str(e),
        )


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
            
        Raises:
            ImageGenerationError: If the response is blocked, empty, or API fails
        """
        # Build content: text + optional images
        contents = [message]
        if images:
            contents.extend(images)

        log.info(f"Sending chat message with {len(images) if images else 0} images")
        log.debug(f"Message: {message[:200]}...")

        try:
            response = chat.send_message(contents)
        except Exception as e:
            # Convert API exceptions to ImageGenerationError with proper error codes
            log.error(f"Gemini API error: {e}", exc_info=True)
            raise ImageGenerationError.from_exception(e)

        # Extract image from response. Use the *last* image part so that in
        # multi-turn edits we return the newly generated image, not an earlier
        # part (e.g. reference echo or thinking image). See research scripts
        # that skip thought parts and take the final image.
        generated_image = None
        
        # Handle case where response.parts is None (blocked or empty response)
        if response.parts is None:
            error_info = self._extract_error_info(response)
            log.warning(f"Gemini returned empty response: {error_info}")
            raise ImageGenerationError(**error_info)
        
        for part in response.parts:
            if getattr(part, "thought", False):
                continue
            if part.text is not None:
                log.debug(f"Chat response text: {part.text[:200]}...")
            if part.inline_data is not None:
                generated_image = part.as_image()
        
        if generated_image is not None:
            log.info("Image generated successfully from chat")
        else:
            # We got parts but no image - check for finish reason
            error_info = self._extract_error_info(response)
            if error_info["error_code"] != ImageGenerationError.UNKNOWN:
                log.warning(f"No image in response: {error_info}")
                raise ImageGenerationError(**error_info)

        return generated_image, response
    
    def _extract_error_info(self, response: GenerateContentResponse) -> dict:
        """
        Extract detailed error information from a Gemini response.
        
        Args:
            response: The Gemini API response
            
        Returns:
            Dict with message, error_code, and details for ImageGenerationError
        """
        # Check for prompt feedback (input was blocked)
        if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
            feedback = response.prompt_feedback
            block_reason = getattr(feedback, 'block_reason', None)
            
            if block_reason:
                block_reason_str = str(block_reason)
                log.warning(f"Prompt blocked: {block_reason_str}")
                
                if "SAFETY" in block_reason_str.upper():
                    return {
                        "message": "Your request was blocked by safety filters. Please modify your prompt and try again.",
                        "error_code": ImageGenerationError.SAFETY_BLOCK,
                        "details": f"Block reason: {block_reason_str}",
                    }
                elif "OTHER" in block_reason_str.upper():
                    return {
                        "message": "Your request could not be processed. It may violate content policies. Please try a different prompt.",
                        "error_code": ImageGenerationError.BLOCKED_PROMPT,
                        "details": f"Block reason: {block_reason_str}",
                    }
                else:
                    return {
                        "message": f"Your prompt was blocked: {block_reason_str}. Please modify and try again.",
                        "error_code": ImageGenerationError.BLOCKED_PROMPT,
                        "details": f"Block reason: {block_reason_str}",
                    }
        
        # Check candidates for finish reason (output was blocked)
        if hasattr(response, 'candidates') and response.candidates:
            for candidate in response.candidates:
                finish_reason = getattr(candidate, 'finish_reason', None)
                if finish_reason:
                    finish_reason_str = str(finish_reason)
                    log.warning(f"Generation stopped: {finish_reason_str}")
                    
                    if "SAFETY" in finish_reason_str.upper():
                        return {
                            "message": "The generated image was blocked by safety filters. Please try a different prompt.",
                            "error_code": ImageGenerationError.SAFETY_BLOCK,
                            "details": f"Finish reason: {finish_reason_str}",
                        }
                    elif "RECITATION" in finish_reason_str.upper():
                        return {
                            "message": "The request was blocked due to potential copyright concerns. Please try a more unique prompt.",
                            "error_code": ImageGenerationError.RECITATION,
                            "details": f"Finish reason: {finish_reason_str}",
                        }
                    elif "STOP" not in finish_reason_str.upper():
                        return {
                            "message": f"Image generation stopped: {finish_reason_str}. Please try again.",
                            "error_code": ImageGenerationError.BLOCKED_RESPONSE,
                            "details": f"Finish reason: {finish_reason_str}",
                        }
        
        # Default: empty response with no clear reason
        return {
            "message": "No image was generated. The AI could not process your request. Please try a different prompt.",
            "error_code": ImageGenerationError.EMPTY_RESPONSE,
            "details": "Response contained no image data",
        }

