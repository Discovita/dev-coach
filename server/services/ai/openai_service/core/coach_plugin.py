"""
OpenAIServicePlugin

This plugin provides a legacy-compatible interface for the new modular OpenAIService.
It exposes a `generate` method that matches the old provider's interface, but delegates
all logic to the new service.

Usage:
    service = OpenAIService(api_key=..., organization=...)
    plugin = OpenAIServicePlugin(service)
    result = await plugin.generate(prompt, system_message, response_format, ...)
"""

from typing import Optional, Type
from pydantic import BaseModel
from apps.chat_messages.models import ChatMessage
from models.CoachChatResponse import CoachChatResponse
from models.SentinelChatResponse import SentinelChatResponse
from services.ai.openai_service.core.base import OpenAIService
from enums.ai import AIModel
from services.ai.base import AIService
from enums.ai import AIProvider

from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


class OpenAIServicePlugin(AIService):
    """
    Plugin/adapter for OpenAIService, providing a legacy-compatible interface for the Coach.
    Inherits from AIService to ensure compatibility with the AI service interface expected by the application.
    Implements the required abstract methods: generate, get_provider_name.
    """

    def __init__(self, service: OpenAIService):
        """
        Initialize the plugin with an instance of the new OpenAIService.
        """
        self.service = service

    def generate(
        self,
        coach_prompt: str,
        chat_history: list[ChatMessage],
        response_format: Type[BaseModel],
        model: AIModel,
        temperature: Optional[float] = None,
        images: Optional[list] = None,
        **kwargs,
    ) -> CoachChatResponse:
        """
        Generate a response using the new OpenAIService, matching the old interface.

        Step-by-step:
        1. Determine the correct model and temperature.
        2. Determine the correct token parameter for the model.
        3. Build OpenAI-style messages.
        4. Prepare parameters for the completion call.
        5. Call the appropriate completion method.
        6. Parse and return the response.
        """
        temperature = (
            temperature
            if temperature is not None
            else getattr(self.service, "temperature", 0.2)
        )

        token_param = AIModel.get_token_param_name(model)
        max_tokens = kwargs.get(token_param, AIModel.get_default_token_limit(model))

        # NOTE: Removed chat history because the messages I want to send in are being added manually already as part of the prompt with added Action context between the messages. It is believed that having the messages twice is negatively affecting the performance of the Coach.
        messages = self.service.create_messages(
            system_message=coach_prompt,
            # messages=chat_history,
            images=images,
        )

        completion_params = {
            "model": model.value,
            "temperature": temperature,
            token_param: max_tokens,
        }
        for key, value in kwargs.items():
            if key not in completion_params and key not in [
                "max_tokens",
                "max_completion_tokens",
                "temperature",
                "response_format",
                "images",
            ]:
                completion_params[key] = value

        if (
            response_format
            and isinstance(response_format, type)
            and issubclass(response_format, BaseModel)
        ):
            response = self.service.create_structured_chat_completion(
                messages=messages,
                response_format=response_format,
                **completion_params,
            )
            parsed = self.parse_response(
                response=response.choices[0].message.parsed,
                dynamic_model=response_format,
            )
            log.debug(f"OenAI response: {parsed}")
            log.debug(f"OpenAI response: {type(parsed)}")
            return parsed

    def call_sentinel(
        self,
        sentinel_prompt: str,
        response_format: Type[BaseModel],
        model: AIModel,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> SentinelChatResponse:
        """
        Generate a response using the new OpenAIService.
        """
        temperature = (
            temperature
            if temperature is not None
            else getattr(self.service, "temperature", 0.2)
        )

        # 2. Token parameter
        token_param = AIModel.get_token_param_name(model)
        max_tokens = kwargs.get(token_param, AIModel.get_default_token_limit(model))

        # 3. Build messages
        messages = self.service.create_messages(
            system_message=sentinel_prompt,
        )

        # 4. Prepare params
        completion_params = {
            "model": model.value,
            "temperature": temperature,
            token_param: max_tokens,
        }
        for key, value in kwargs.items():
            if key not in completion_params and key not in [
                "max_tokens",
                "max_completion_tokens",
                "temperature",
                "response_format",
                "images",
            ]:
                completion_params[key] = value

        # 5. Call completion
        if (
            response_format
            and isinstance(response_format, type)
            and issubclass(response_format, BaseModel)
        ):
            response = self.service.create_structured_chat_completion(
                messages=messages,
                response_format=response_format,
                **completion_params,
            )
            # 6. Parse and return
            parsed = self.parse_sentinel_response(
                response=response.choices[0].message.parsed,
                dynamic_model=response_format,
            )
            log.debug(f"OenAI response: {parsed}")
            log.debug(f"OpenAI response: {type(parsed)}")
            return parsed

    def get_provider_name(self) -> AIProvider:
        """
        Get the name of the provider being used.
        Returns AIProvider.OPENAI for this plugin.
        """
        return AIProvider.OPENAI
