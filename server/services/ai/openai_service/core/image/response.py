"""Processing utilities for image generation responses."""

import logging
from typing import List, Dict, Any, Optional

log = logging.getLogger(__name__)


def process_image_response(
    response: Any, save_to_path: Optional[str] = None, save_image_func=None
) -> List[Dict[str, Any]]:
    """
    Process the response from the OpenAI API for image generation.
    
    Args:
        response: Response object from OpenAI API
        save_to_path: Directory to save images to, if applicable
        save_image_func: Function to use for saving images
        
    Returns:
        List of processed image data dictionaries
    """
    if not hasattr(response, "data"):
        log.warning("Response does not contain 'data' attribute")
        return []
    
    result = []
    
    for i, img_data in enumerate(response.data):
        img_result = {}
        
        # Copy all available properties
        if hasattr(img_data, "url") and img_data.url:
            img_result["url"] = img_data.url
            
        if hasattr(img_data, "b64_json") and img_data.b64_json:
            img_result["b64_json"] = img_data.b64_json
            
        if hasattr(img_data, "revised_prompt") and img_data.revised_prompt:
            img_result["revised_prompt"] = img_data.revised_prompt
            
        # Save the image if requested and we have the necessary function
        if save_to_path and save_image_func and hasattr(img_data, "b64_json") and img_data.b64_json:
            try:
                local_path = save_image_func(img_data, save_to_path, i)
                if local_path:
                    img_result["local_path"] = local_path
            except Exception as e:
                log.error(f"Failed to save image: {e}")
        
        result.append(img_result)
        
    return result 