"""
AI Service Factory

Single entry point for creating AI service instances.
Resolves the correct concrete implementation based on the requested model.

To add a new provider:
  1. Create a new class in services/ai/ that inherits from AIService.
  2. Add the new provider's elif branch below.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parents[3] / ".env")

from enums.ai import AIModel, AIProvider
from services.ai.base import AIService
from services.ai.openai_service import OpenAIService
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


class AIServiceFactory:
    """
    Factory for creating AIService instances.

    Usage:
        service = AIServiceFactory.create(AIModel.GPT_4O)
        response = service.generate(prompt, history, ResponseFormat, model)
    """

    @staticmethod
    def create(model: AIModel) -> AIService:
        """
        Return a concrete AIService for the given model.

        Raises:
            NotImplementedError: if the model's provider is not yet implemented.
            ValueError: if the API key is missing or the provider is unknown.
        """
        log.debug(f"Creating AI service for model: {model}")
        provider = AIModel.get_provider(model)

        if provider == AIProvider.ANTHROPIC:
            raise NotImplementedError("AnthropicService is not yet implemented.")

        if provider == AIProvider.OPENAI:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required.")
            return OpenAIService(api_key=api_key)

        raise ValueError(f"Unsupported AI provider: {provider} (model={model.value})")
