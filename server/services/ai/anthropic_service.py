"""
Anthropic AI Service Module

This module provides the implementation of AIService for Anthropic's Claude models.
It handles the communication with Anthropic's API using the AnthropicHelper.

TODO: Need to implement this if we want to support Claude
"""

from typing import Optional, Type
import os
from dotenv import load_dotenv
import re

from pydantic import BaseModel

from enums.ai import AIModel, AIProvider

# from cws_helpers.anthropic_helper import AnthropicHelper
from models.CoachChatResponse import CoachChatResponse
from services.ai.base import AIService


from services.logger import configure_logging

log = configure_logging(__name__)

load_dotenv()


class AnthropicService(AIService):
    """
    Implementation of AIService for Anthropic's Claude models.
    This service uses the AnthropicHelper to interact with Claude models.
    """

    def __init__(self):
        self.ai_model = "claude-2"
        self.temperature = 0.2

        if isinstance(self.ai_model, str):
            model = AIModel.from_string(self.ai_model)
        else:
            model = self.ai_model

        self.model = model
        self.model_name = model.value

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is required (set in .env file or environment)"
            )

        # try:
        #     self.helper = AnthropicHelper(api_key=api_key, model=self.model_name)
        #     log.info(
        #         f"Initialized Anthropic service with model: {self.model_name}, temperature: {self.temperature}"
        #     )
        # except Exception as e:
        #     log.error(f"Failed to initialize Anthropic service: {e}")
        #     raise

    def generate(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        response_format: Type[BaseModel] = None,
        **kwargs,
    ) -> CoachChatResponse:
        """Generate text using Claude."""
        try:
            max_tokens = kwargs.get("max_tokens", 4096)

            response = self.helper.create_message(
                prompt=prompt,
                system=system_message,
                max_tokens=max_tokens,
                temperature=self.temperature,
            )
            response = self.parse_response(
                response=response, dynamic_model=response_format
            )

            return response
        except Exception as e:
            log.error(f"Error generating text with Anthropic: {e}")
            raise

    def get_provider_name(self) -> AIProvider:
        """Get the name of the provider being used."""
        return AIProvider.ANTHROPIC
