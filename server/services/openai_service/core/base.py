"""
Base OpenAIService class for interacting with the OpenAI API.

This module contains the main OpenAIService class which provides
a simplified interface to OpenAI's API.
"""

from openai import OpenAI
from typing import Annotated, Optional
import logging
from ..utils.model_utils import check_dependency_versions
from .messages import MessageMixin
from .chat.structured import StructuredCompletionMixin
from .chat.generic import GenericChatCompletionMixin
from .image import ImageGenerationMixin

log = logging.getLogger(__name__)

class OpenAIService(
    MessageMixin, StructuredCompletionMixin, GenericChatCompletionMixin, ImageGenerationMixin
):
    """
    A helper class for interacting with the OpenAI API.

    Provides methods for creating chat completions with support for:
    - Basic text responses
    - Image inputs
    - JSON mode
    - Structured outputs using JSON schema
    - Pydantic model parsing
    - Beta structured outputs with automatic parsing
    - Image generation with DALL-E models
    - Image editing and variations (DALL-E 2 only)

    This class initializes the OpenAI client with your API key and
    organization, and provides methods to interact with the API.
    """

    def __init__(
        self,
        api_key: Annotated[str, "The OpenAI API Key you wish to use"],
        organization: Optional[Annotated[str, "Your OpenAI organization ID (optional)"]] = None,
    ):
        """
        Initialize the OpenAI helper with your API key and organization.

        Parameters
        ----------
        api_key : str
            Your OpenAI API key
        organization : str, optional
            Your OpenAI organization ID. If not provided, the default organization
            associated with your API key will be used.
        """
        self.client = OpenAI(api_key=api_key, organization=organization)

        check_dependency_versions()
