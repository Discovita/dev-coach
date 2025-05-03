"""Validation utilities for image generation parameters."""

import logging
from typing import Optional, Union, Dict, Any
from ...models.image import ImageSize, ImageQuality, ImageStyle, ImageResponseFormat, ImageModel

log = logging.getLogger(__name__)


def validate_and_process_image_params(
    prompt: str,
    model: Union[str, ImageModel] = None,
    n: Optional[int] = None,
    size: Optional[Union[str, ImageSize]] = None,
    quality: Optional[Union[str, ImageQuality]] = None,
    style: Optional[Union[str, ImageStyle]] = None,
    response_format: Optional[Union[str, ImageResponseFormat]] = None,
    save_to_path: Optional[str] = None,
    user: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Validate and process parameters for image generation.
    
    Args:
        prompt: Text prompt for image generation
        model: DALL-E model to use
        n: Number of images to generate
        size: Image size
        quality: Image quality (DALL-E 3 only)
        style: Image style (DALL-E 3 only)
        response_format: Format for the response
        save_to_path: Directory to save images to
        user: Unique identifier for end-user
        
    Returns:
        Dict containing processed parameters
    """
    # Convert model enum to string value if needed
    model_value = model.value if isinstance(model, ImageModel) else model
    if not model_value:
        model_value = ImageModel.default_model()
        
    # Check prompt length restrictions
    if model_value == ImageModel.DALL_E_2.value and len(prompt) > 1000:
        log.warning(
            f"Prompt exceeds maximum length of 1000 characters for {model_value}. It will be truncated."
        )
        prompt = prompt[:1000]
    elif model_value == ImageModel.DALL_E_3.value and len(prompt) > 4000:
        log.warning(
            f"Prompt exceeds maximum length of 4000 characters for {model_value}. It will be truncated."
        )
        prompt = prompt[:4000]

    # Override response_format to b64_json if saving to disk
    actual_response_format = response_format
    if save_to_path and not response_format:
        actual_response_format = "b64_json"
        log.info("Using b64_json response format for saving images to disk")

    # Convert enums to string values if needed
    size_value = size.value if isinstance(size, ImageSize) else size
    quality_value = quality.value if isinstance(quality, ImageQuality) else quality
    style_value = style.value if isinstance(style, ImageStyle) else style
    response_format_value = (
        actual_response_format.value
        if isinstance(actual_response_format, ImageResponseFormat)
        else actual_response_format
    )

    # Parameter validation based on model
    if model_value == ImageModel.DALL_E_3.value:
        if n and n > 1:
            log.warning("DALL-E 3 only supports n=1. Setting n=1.")
            n = 1

        valid_sizes = (
            ImageSize.dall_e_3_sizes()
            if hasattr(ImageSize, "dall_e_3_sizes")
            else ["1024x1024", "1792x1024", "1024x1792"]
        )

        if size_value and size_value not in valid_sizes:
            log.warning(
                f"DALL-E 3 doesn't support size {size_value}. Defaulting to 1024x1024."
            )
            size_value = "1024x1024"

    elif model_value == ImageModel.DALL_E_2.value:
        valid_sizes = (
            ImageSize.dall_e_2_sizes()
            if hasattr(ImageSize, "dall_e_2_sizes")
            else ["256x256", "512x512", "1024x1024"]
        )

        if size_value and size_value not in valid_sizes:
            log.warning(
                f"DALL-E 2 doesn't support size {size_value}. Defaulting to 1024x1024."
            )
            size_value = "1024x1024"

        # Quality parameter only applies to DALL-E 3
        if quality:
            log.warning(
                "Quality parameter only applies to DALL-E 3. It will be ignored."
            )
            quality_value = None

        # Style parameter only applies to DALL-E 3
        if style:
            log.warning(
                "Style parameter only applies to DALL-E 3. It will be ignored."
            )
            style_value = None

    # Create request parameters, only adding non-None values
    params = {"prompt": prompt}

    if model_value is not None:
        params["model"] = model_value
    if n is not None:
        params["n"] = n
    if size_value is not None:
        params["size"] = size_value
    if response_format_value is not None:
        params["response_format"] = response_format_value
    if user is not None:
        params["user"] = user

    # Add DALL-E 3 specific parameters if applicable
    if model_value == ImageModel.DALL_E_3.value:
        if quality_value is not None:
            params["quality"] = quality_value
        if style_value is not None:
            params["style"] = style_value
            
    return params 