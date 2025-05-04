"""
AI Service Factory

This module provides a factory class for creating AI service instances.
The factory abstracts the creation logic, allowing the rest of the application
to request AI services without knowing the specific implementation details.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env in project root
load_dotenv(Path(__file__).parents[3] / ".env")
from services.logger import configure_logging


log = configure_logging(__name__)

# Import the AIService interface and implementations
from services.ai import AIService, AnthropicService
from enums.ai import AIModel, AIProvider

# Import the new OpenAIService and the plugin/adapter for legacy compatibility
from services.ai.openai_service.core.base import OpenAIService
from services.ai.openai_service.core.coach_plugin import OpenAIServicePlugin


class AIServiceFactory:
    """
    Factory class for creating AI service instances.˝

    This class provides static methods to create instances of different AI services
    based on the configuration in the Services context.
    """

    @staticmethod
    def create(model: AIModel) -> AIService:
        """
        Create an AI service instance based on the LLM model.
        This returns a plugin/adapter for OpenAI models, providing a legacy-compatible interface.
        Step-by-step:
        1. Determine the provider for the requested model.
        2. If Anthropic, raise NotImplementedError.
        3. If OpenAI, instantiate the new OpenAIService with API key/org.
        4. Wrap the service in OpenAIServicePlugin to provide the generate() interface.
        5. Return the plugin instance.
        """
        log.info(f"Creating AI service for model: {model}")
        try:
            provider = AIModel.get_provider(model)
            if provider == AIProvider.ANTHROPIC:
                raise NotImplementedError("AnthropicService is not yet implemented.")

            elif provider == AIProvider.OPENAI:
                log.debug("Creating OpenAIService")
                openai_api_key = os.getenv("OPENAI_API_KEY")
                if not openai_api_key:
                    raise ValueError("OPENAI_API_KEY is required")
                # Instantiate the new OpenAIService
                service = OpenAIService(api_key=openai_api_key)
                # Wrap in the plugin for legacy-compatible interface
                return OpenAIServicePlugin(service)

            else:
                raise ValueError(f"Unsupported AI provider for model {model.value}")

        except ValueError as e:
            raise ValueError(f"Error creating AI service: {str(e)}")
