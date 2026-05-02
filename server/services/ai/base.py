"""
AI Service Base Module

Defines the AIService abstract base class — the contract all AI service
implementations must satisfy.

Current implementations:
    OpenAIService  (services/ai/openai_service.py)

To add a new provider (e.g. Anthropic), create a new class that inherits from
AIService, implement the abstract methods, and register it in AIServiceFactory.

To add a new capability (e.g. streaming), declare it here as an abstract method
and implement it on each concrete service.
"""

import json
import re
from abc import ABC, abstractmethod
from typing import Optional, Type, Union

from pydantic import BaseModel

from apps.chat_messages.models import ChatMessage
from enums.ai import AIProvider
from models.CoachChatResponse import CoachChatResponse
from models.SentinelChatResponse import SentinelChatResponse
from services.logger import configure_logging

log = configure_logging(__name__)


class AIService(ABC):
    """
    Abstract base class defining the interface for all AI service implementations.

    Callers interact exclusively with this interface. The concrete implementation
    is resolved by AIServiceFactory.create(model) and is an implementation detail.
    """

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def generate(
        self,
        coach_prompt: Optional[str],
        chat_history: list[ChatMessage],
        response_format: Type[BaseModel],
        model,
        **kwargs,
    ) -> CoachChatResponse:
        """Generate a coach response for the given prompt and chat history."""
        pass

    @abstractmethod
    def call_sentinel(
        self,
        sentinel_prompt: Optional[str],
        response_format: Type[BaseModel],
        model,
        **kwargs,
    ) -> SentinelChatResponse:
        """Call the sentinel service to extract structured notes from the conversation."""
        pass

    @abstractmethod
    def get_provider_name(self) -> AIProvider:
        """Return the AIProvider enum value for this implementation."""
        pass

    # -------------------------------------------------------------------------
    # Shared static helpers (used by all concrete implementations)
    # -------------------------------------------------------------------------

    @staticmethod
    def extract_json_from_response(response: str) -> dict:
        """
        Extract the first JSON object from a string, even if surrounded by text
        or markdown code fences.

        Raises ValueError if no valid JSON object is found.
        """
        response = response.strip()
        if response.startswith("```"):
            response = re.sub(r"^```(?:json)?", "", response, flags=re.IGNORECASE).strip()
            response = re.sub(r"```$", "", response).strip()
        start = response.find("{")
        end = response.rfind("}")
        if start == -1 or end == -1 or end < start:
            raise ValueError("No valid JSON object found in response.")
        json_str = response[start : end + 1]
        try:
            return json.loads(json_str)
        except Exception as e:
            raise ValueError(f"Failed to parse JSON: {e}\nExtracted: {json_str}")

    @staticmethod
    def parse_response(
        response: Union[str, BaseModel, dict],
        dynamic_model: Type[BaseModel],
    ) -> CoachChatResponse:
        """
        Standard pipeline: parse any LLM output into a CoachChatResponse.

        Accepts a raw string (with optional JSON extraction), a dict, or a
        Pydantic model instance.
        """
        if isinstance(response, str):
            response = AIService.extract_json_from_response(response)
        if isinstance(response, dynamic_model):
            validated = response
        else:
            validated = dynamic_model.model_validate(response)
        return CoachChatResponse.model_validate(validated.model_dump())

    @staticmethod
    def parse_sentinel_response(
        response: Union[str, BaseModel, dict],
        dynamic_model: Type[BaseModel],
    ) -> SentinelChatResponse:
        """
        Standard pipeline: parse any LLM output into a SentinelChatResponse.

        Accepts a raw string (with optional JSON extraction), a dict, or a
        Pydantic model instance.
        """
        if isinstance(response, str):
            response = AIService.extract_json_from_response(response)
        if isinstance(response, dynamic_model):
            validated = response
        else:
            validated = dynamic_model.model_validate(response)
        return SentinelChatResponse.model_validate(validated.model_dump())
