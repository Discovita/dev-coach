"""
Mixin for message-related functionality in OpenAIService.
"""

from typing import Any, List, Optional
from openai.types.chat import ChatCompletionMessageParam

from apps.chat_messages.models import ChatMessage

from .utils import create_messages as create_messages_util


class MessageMixin:
    """
    Mixin providing message-related functionality for OpenAIService.
    """

    def create_messages(
        self,
        system_message: Optional[str] = None,
        prompt: Optional[str] = None,
        messages: Optional[List[ChatMessage]] = None,
        images: Optional[List[str]] = None,
    ) -> List[ChatCompletionMessageParam]:
        """
        Create a list of messages for the chat completion API.

        This method formats the user prompt, system message, images,
        and conversation history into the format expected by OpenAI's API.

        Parameters
        ----------
        prompt : str, optional
            The user prompt/query text (not required if messages is provided)
        system_message : Optional[str]
            Optional system message to set context
        images : Optional[List[str]]
            Optional list of image paths to include
        messages : Optional[List[Any]]
            Optional list of Message objects with role and content attributes

        Returns
        -------
        List[ChatCompletionMessageParam]
            Formatted messages ready for API use
        """
        return create_messages_util(
            system_message=system_message,
            prompt=prompt,
            messages=messages,
            images=images,
        )
