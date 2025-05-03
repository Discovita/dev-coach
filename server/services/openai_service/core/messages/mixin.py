"""
Mixin for message-related functionality in OpenAIService.
"""

from typing import List, Optional
from openai.types.chat import ChatCompletionMessageParam

from .utils import create_messages as create_messages_util


class MessageMixin:
    """
    Mixin providing message-related functionality for OpenAIService.
    """

    def create_messages(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        images: Optional[List[str]] = None
    ) -> List[ChatCompletionMessageParam]:
        """
        Create a list of messages for the chat completion API.
        
        This method formats the user prompt, system message, and images
        into the format expected by OpenAI's API.
        
        Parameters
        ----------
        prompt : str
            The user prompt/query text
        system_message : Optional[str]
            Optional system message to set context
        images : Optional[List[str]]
            Optional list of image paths to include
            
        Returns
        -------
        List[ChatCompletionMessageParam]
            Formatted messages ready for API use
        """
        return create_messages_util(prompt=prompt, system_message=system_message, images=images) 