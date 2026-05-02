"""
parse_coach_response

Extracts the parsed Pydantic object from a raw ParsedChatCompletion and
validates it into a CoachChatResponse via AIService.parse_response.
"""

from typing import Type

from openai.types.chat import ParsedChatCompletion
from pydantic import BaseModel

from models.CoachChatResponse import CoachChatResponse
from services.ai.base import AIService


def parse_coach_response(
    completion: ParsedChatCompletion,
    response_format: Type[BaseModel],
) -> CoachChatResponse:
    """
    Convert a ParsedChatCompletion into a CoachChatResponse.

    Parameters
    ----------
    completion : ParsedChatCompletion
        The raw completion returned by structured_completion.
    response_format : Type[BaseModel]
        The Pydantic model class used as the response_format for the API call.
        Must be compatible with CoachChatResponse (i.e. a subclass or duck-type
        that model_dump() can convert).

    Returns
    -------
    CoachChatResponse
        Validated response model containing the coach message and any actions.
    """
    raw = completion.choices[0].message.parsed
    return AIService.parse_response(response=raw, dynamic_model=response_format)
