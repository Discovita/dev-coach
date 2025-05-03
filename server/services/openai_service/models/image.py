"""
Model classes for image generation functionality.

This module contains enums and models used for image generation
with OpenAI's DALL-E models.

Note: This implementation currently supports only image generation,
not image editing or variations.
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Union, Literal


class ImageSize(str, Enum):
    """
    Enum for supported image sizes in DALL-E models.
    
    Used in:
    - openai_service/core/image/mixin.py - for specifying image dimensions
    
    DALL-E 3 supports:
    - 1024x1024 (square)
    - 1792x1024 (landscape)
    - 1024x1792 (portrait)
    
    DALL-E 2 supports:
    - 256x256 (small square)
    - 512x512 (medium square)
    - 1024x1024 (large square)
    """
    # DALL-E 2 sizes
    SQUARE_256 = "256x256"
    SQUARE_512 = "512x512"
    SQUARE_1024 = "1024x1024"
    
    # DALL-E 3 additional sizes
    LANDSCAPE_1792x1024 = "1792x1024"
    PORTRAIT_1024x1792 = "1024x1792"
    
    @classmethod
    def dall_e_2_sizes(cls) -> List[str]:
        """Return a list of supported sizes for DALL-E 2"""
        return [cls.SQUARE_256.value, cls.SQUARE_512.value, cls.SQUARE_1024.value]
    
    @classmethod
    def dall_e_3_sizes(cls) -> List[str]:
        """Return a list of supported sizes for DALL-E 3"""
        return [
            cls.SQUARE_1024.value, 
            cls.LANDSCAPE_1792x1024.value, 
            cls.PORTRAIT_1024x1792.value
        ]


class ImageQuality(str, Enum):
    """
    Enum for image quality options in DALL-E 3.
    
    Used in:
    - openai_service/core/image/mixin.py - for specifying image quality
    
    DALL-E 3 supports:
    - standard (default, faster generation)
    - hd (enhanced detail, better for complex images)
    
    Note: This parameter is only applicable to DALL-E 3 models.
    """
    STANDARD = "standard"
    HD = "hd"


class ImageStyle(str, Enum):
    """
    Enum for image style options in DALL-E 3.
    
    Used in:
    - openai_service/core/image/mixin.py - for specifying image style
    
    DALL-E 3 supports:
    - vivid (default, hyper-real and dramatic images)
    - natural (more natural, less hyper-real looking images)
    
    Note: This parameter is only applicable to DALL-E 3 models.
    """
    VIVID = "vivid"
    NATURAL = "natural"


class ImageResponseFormat(str, Enum):
    """
    Enum for response format options when generating images.
    
    Used in:
    - openai_service/core/image/mixin.py - for specifying response format
    
    - url: Return a URL to the generated image (expires after 1 hour)
    - b64_json: Return base64-encoded JSON string of the image (for direct use or saving)
    
    When saving images locally, b64_json is automatically used for efficiency.
    """
    URL = "url"
    B64_JSON = "b64_json"


class ImageModel(str, Enum):
    """
    Enum for supported image generation models.
    
    Used in:
    - openai_service/core/image/mixin.py - for specifying which model to use
    
    Features by model:
    - DALL-E 3: Higher quality, larger sizes, automatic prompt revision
    - DALL-E 2: More options (more control in prompting)
    
    Note: While DALL-E 2 supports image editing and variations in the OpenAI API,
    these features are not currently implemented in this library.
    """
    DALL_E_2 = "dall-e-2"
    DALL_E_3 = "dall-e-3"
    
    @classmethod
    def default_model(cls) -> str:
        """Return the recommended default model"""
        return cls.DALL_E_3.value 