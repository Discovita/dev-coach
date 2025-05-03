"""
OpenAI Helper module for interacting with OpenAI's API.

This module provides a simplified interface for making requests to OpenAI's API,
with support for text completions, image inputs, JSON mode, structured outputs,
and streaming responses.

Usage:
    from openai_service import OpenAIService

    helper = OpenAIService(api_key="your_api_key", organization="your_org_id")
    response = helper.create_chat_completion(prompt="Hello, world!")

    # You can also access the AIModel enum for model-specific logic
    from openai_service import AIModel

    # Check if a model supports structured outputs
    supports_structured = AIModel.supports_structured_outputs("gpt-4o")

    # Get the appropriate token parameter name for a model
    token_param = AIModel.get_token_param_name("o3-mini")  # Returns "max_completion_tokens"
    
    # Generate images using DALL-E models
    from openai_service import OpenAIService, ImageSize, ImageQuality, ImageStyle, ImageModel
    
    helper = OpenAIService(api_key="your_api_key")
    images = helper.generate_image(
        prompt="A futuristic city with flying cars",
        model=ImageModel.DALL_E_3,
        size=ImageSize.LANDSCAPE_1792x1024,
        quality=ImageQuality.HD,
        style=ImageStyle.NATURAL
    )
"""

from .core import OpenAIService
from .enums import AIModel, AIProvider
from .models import ImageSize, ImageQuality, ImageResponseFormat, ImageModel, ImageStyle

__all__ = [
    "OpenAIService", 
    "AIModel", 
    "AIProvider",
    "ImageSize",
    "ImageQuality",
    "ImageResponseFormat",
    "ImageModel",
    "ImageStyle"
]
