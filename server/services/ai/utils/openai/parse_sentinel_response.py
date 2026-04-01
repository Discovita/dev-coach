"""
parse_sentinel_response

Extracts the parsed Pydantic object from a raw ParsedChatCompletion and
validates it into a SentinelChatResponse via AIService.parse_sentinel_response.
"""

from typing import Type

from openai.types.chat import ParsedChatCompletion
from pydantic import BaseModel

from models.SentinelChatResponse import SentinelChatResponse
from services.ai.base import AIService


def parse_sentinel_response(
    completion: ParsedChatCompletion,
    response_format: Type[BaseModel],
) -> SentinelChatResponse:
    """
    Convert a ParsedChatCompletion into a SentinelChatResponse.

    Parameters
    ----------
    completion : ParsedChatCompletion
        The raw completion returned by structured_completion.
    response_format : Type[BaseModel]
        The Pydantic model class used as the response_format for the API call.
        Must be compatible with SentinelChatResponse.

    Returns
    -------
    SentinelChatResponse
        Validated response model containing any sentinel note actions.
    """
    raw = completion.choices[0].message.parsed
    return AIService.parse_sentinel_response(response=raw, dynamic_model=response_format)
