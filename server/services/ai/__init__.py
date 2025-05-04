"""
AI Service Package

This package provides service classes for interacting with different AI models.
It includes implementations for Anthropic's Claude and OpenAI's GPT models,
along with a factory class to simplify service creation.

The package follows a dependency injection pattern, allowing different implementations
to be swapped without changing the core generation logic.
"""

from services.ai.base import AIService
from services.ai.anthropic_service import AnthropicService
from services.ai.openai_service import OpenAIService
from services.ai.ai_service_factory import AIServiceFactory

# Export these classes so they can be imported directly from services.ai
__all__ = [
    "AIServiceFactory",
    "AIService",
    "AnthropicService",
    "OpenAIService",
]
