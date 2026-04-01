"""
AI Service Package

Provides the AIService interface and a factory for creating concrete implementations.

Public exports:
    AIServiceFactory  — use this to obtain a service instance
    AIService         — the abstract base class (for type hints / new implementations)
    OpenAIService     — the concrete OpenAI implementation
"""

from services.ai.ai_service_factory import AIServiceFactory
from services.ai.base import AIService
from services.ai.openai_service import OpenAIService

__all__ = [
    "AIServiceFactory",
    "AIService",
    "OpenAIService",
]
