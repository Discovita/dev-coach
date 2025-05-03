"""
Response type definitions for OpenAI API interactions.

This module provides type definitions and helpers for handling
various response formats from the OpenAI API.
"""

from typing import TypeVar, Type, Generic, Optional, Protocol
from openai.types.chat import ChatCompletion

import logging

log = logging.getLogger(__name__)

ResponseFormatT = TypeVar("ResponseFormatT")


class ParsedChatCompletionProtocol(Protocol, Generic[ResponseFormatT]):
    """Protocol defining the interface we need from ParsedChatCompletion."""

    parsed: Optional[ResponseFormatT]


class FallbackParsedChatCompletion(ChatCompletion, Generic[ResponseFormatT]):
    """
    Fallback implementation of ParsedChatCompletion for older OpenAI SDK versions.

    This class extends ChatCompletion and adds a Generic parameter for response formats.
    """

    parsed: Optional[ResponseFormatT] = None


try:
    from openai.types.chat.parsed_chat_completion import (
        ParsedChatCompletion as OpenAIParsedChatCompletion,
    )

    _has_parsed_completion = True
    log.debug("Using OpenAI's ParsedChatCompletion for structured outputs")
except ImportError:
    _has_parsed_completion = False
    OpenAIParsedChatCompletion = FallbackParsedChatCompletion
    log.debug("ParsedChatCompletion not available, using fallback implementation")

ParsedChatCompletion = OpenAIParsedChatCompletion


def get_parsed_chat_completion() -> Type:
    """
    Return the appropriate ParsedChatCompletion class.

    This function handles compatibility with different versions of the
    OpenAI Python package.

    Returns
    -------
    Type
        The ParsedChatCompletion class or fallback implementation
    """
    return OpenAIParsedChatCompletion
