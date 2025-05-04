"""
Message utility functions for OpenAI API interactions.

This module provides utility functions for working with chat messages
in the format expected by OpenAI's API.
"""

import logging
from typing import Any, List, Optional

from services.ai.openai_service.core.image.utils import encode_image
from openai.types.chat import ChatCompletionContentPartParam, ChatCompletionMessageParam

from apps.chat_messages.models import ChatMessage

log = logging.getLogger(__name__)


def create_messages(
    system_message: Optional[str] = None,
    prompt: str = None,
    messages: Optional[List[ChatMessage]] = None,
    images: Optional[List[str]] = None,
) -> List[ChatCompletionMessageParam]:
    """
    Create a list of messages for the chat completion API.
    """
    result_messages = []

    # Add system message if provided
    if system_message:
        result_messages.append({"role": "system", "content": system_message})

    # Add messages from history if provided
    if messages:
        for msg in messages:
            # Convert "coach" role to "assistant" for OpenAI API compatibility
            role = "assistant" if msg.role == "coach" else msg.role
            result_messages.append({"role": role, "content": msg.content})

    # Add new prompt if provided
    if prompt:
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

            result_messages.append({"role": "user", "content": content_parts})
        else:
            result_messages.append({"role": "user", "content": prompt})

    return result_messages
