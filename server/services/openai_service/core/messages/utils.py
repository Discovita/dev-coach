"""
Message utility functions for OpenAI API interactions.

This module provides utility functions for working with chat messages
in the format expected by OpenAI's API.
"""

from typing import List, Optional
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionContentPartParam,
)

import logging
from openai_service.utils.image import encode_image

log = logging.getLogger(__name__)


def create_messages(
    prompt: str,
    system_message: Optional[str] = None,
    images: Optional[List[str]] = None,
) -> List[ChatCompletionMessageParam]:
    """
    Create a list of messages for the chat completion API.

    This function formats the user prompt, system message, and images
    into the format expected by OpenAI's API.

    Parameters
    ----------
        system_message : Optional system message to set context
        prompt : The user prompt/query text
        images : Optional list of image paths or URLs to include

    Returns
    -------
        Formatted messages ready for API use
    """
    messages = []

    if system_message:
        messages.append({"role": "system", "content": system_message})

    if images:
        content_parts: List[ChatCompletionContentPartParam] = []

        content_parts.append({"type": "text", "text": prompt})

        for image_path in images:
            log.debug(f"Adding image from {image_path} to request")
            try:
                if image_path.startswith(("http://", "https://")):
                    image_url = image_path
                else:
                    image_url = encode_image(image_path)

                content_parts.append(
                    {"type": "image_url", "image_url": {"url": image_url}}
                )
            except Exception as e:
                log.error(f"Failed to encode image {image_path}: {str(e)}")
                continue

        messages.append({"role": "user", "content": content_parts})
    else:
        messages.append({"role": "user", "content": prompt})

    return messages
