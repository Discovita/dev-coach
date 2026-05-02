"""
OpenAI Service

Concrete implementation of the AIService interface for OpenAI models.

All per-step logic lives in services.ai.utils.openai — one function per file.
This class wires those utilities together and satisfies the AIService contract.

To add future capabilities (e.g. streaming), add a method here and declare it
on the AIService ABC in base.py.
"""

import logging
from typing import List, Optional, Type

from openai import OpenAI
from pydantic import BaseModel

from apps.chat_messages.models import ChatMessage
from enums.ai import AIModel, AIProvider
from models.CoachChatResponse import CoachChatResponse
from models.SentinelChatResponse import SentinelChatResponse
from services.ai.base import AIService
from services.ai.utils.openai import (
    build_messages,
    parse_coach_response,
    parse_sentinel_response,
    structured_completion,
)

log = logging.getLogger(__name__)


class OpenAIService(AIService):
    """
    Concrete AIService implementation for OpenAI.

    Callers interact with this class through AIServiceFactory.create(model),
    which returns an instance ready to call .generate() or .call_sentinel().

    Public interface (defined on AIService ABC):
        generate(coach_prompt, chat_history, response_format, model) -> CoachChatResponse
        call_sentinel(sentinel_prompt, response_format, model)       -> SentinelChatResponse
        get_provider_name()                                          -> AIProvider
    """

    def __init__(self, api_key: str):
        """
        Initialize with an OpenAI API key.
        The key is sourced from the environment by AIServiceFactory — callers
        do not need to pass it directly.
        """
        self.client = OpenAI(api_key=api_key)

    def generate(
        self,
        coach_prompt: str,
        chat_history: List[ChatMessage],
        response_format: Type[BaseModel],
        model: AIModel,
        temperature: Optional[float] = 0.2,
        **kwargs,
    ) -> CoachChatResponse:
        """
        Generate a structured coach response from OpenAI.

        Sends the coach prompt as a system message (chat history is omitted — it
        is already embedded in the prompt by the PromptManager) and returns a
        parsed CoachChatResponse.
        """
        messages = build_messages(system_message=coach_prompt)
        completion = structured_completion(
            client=self.client,
            messages=messages,
            model=model,
            response_format=response_format,
            temperature=temperature,
            **kwargs,
        )
        parsed = parse_coach_response(completion, response_format)
        log.debug(f"OpenAI response: {parsed}")
        return parsed

    def call_sentinel(
        self,
        sentinel_prompt: str,
        response_format: Type[BaseModel],
        model: AIModel,
        temperature: Optional[float] = 0.2,
        **kwargs,
    ) -> SentinelChatResponse:
        """
        Call the sentinel service to extract structured notes from the conversation.
        """
        messages = build_messages(system_message=sentinel_prompt)
        completion = structured_completion(
            client=self.client,
            messages=messages,
            model=model,
            response_format=response_format,
            temperature=temperature,
            **kwargs,
        )
        parsed = parse_sentinel_response(completion, response_format)
        log.debug(f"OpenAI sentinel response: {parsed}")
        return parsed

    def get_provider_name(self) -> AIProvider:
        """Return the provider identifier for this service."""
        return AIProvider.OPENAI
