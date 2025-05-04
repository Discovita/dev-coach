"""
AI Service Base Module

This module provides the abstract base class that defines the interface
for all AI service implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional, Union, Type

from pydantic import BaseModel
from enums.ai import AIModel, AIProvider
from server.pydantic.CoachChatResponse import CoachChatResponse
import json
import re

from apps.chat_messages.models import ChatMessage
from services.logger import configure_logging

log = configure_logging(__name__)


class AIService(ABC):
    """
    Abstract base class defining the interface for AI services.

    This class defines the methods that all AI services must implement,
    regardless of which AI provider they use.
    """

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    async def generate(
        self,
        coach_prompt: Optional[str],
        chat_history: list[ChatMessage],
        **kwargs,
    ) -> CoachChatResponse:
        """Run a generation prompt."""
        pass

    @abstractmethod
    def get_model_name(self) -> AIModel:
        """Get the name of the model being used."""
        pass

    @abstractmethod
    def get_provider_name(self) -> AIProvider:
        """
        Get the name of the provider being used.

        Returns:
            The name of the provider
        """
        pass

    @staticmethod
    def extract_json_from_response(response: str) -> dict:
        """Extracts the first JSON object found in a string, even if surrounded by text or markdown
        code fences."""
        response = response.strip()
        if response.startswith("```"):
            response = re.sub(
                r"^```(?:json)?", "", response, flags=re.IGNORECASE
            ).strip()
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
        Standard pipeline to parse any LLM output into a consistent CoachChatResponse model.
        """
        if isinstance(response, str):
            response = AIService.extract_json_from_response(response)
        if isinstance(response, dynamic_model):
            validated = response
        else:
            validated = dynamic_model.model_validate(response)
        return CoachChatResponse.model_validate(validated.model_dump())
