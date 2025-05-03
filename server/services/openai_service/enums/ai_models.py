"""
Enum for AI models supported by the OpenAI Helper.

This module contains the AIModel enum for identifying
different AI models and their capabilities.
"""

from enum import Enum
from typing import Union, Set, Optional

import logging

log = logging.getLogger(__name__)

from .ai_providers import AIProvider

from .model_features import (
    STRUCTURED_OUTPUT_MODELS,
    COMPLETION_TOKEN_MODELS,
    UNSUPPORTED_PARAMETERS,
)


class AIModel(Enum):
    """
    Enum representing different AI models supported by the OpenAIService.

    This enum is used to specify which AI model to use when generating text.
    Each model is associated with a specific provider.
    The API will automatically use the latest version of each model.
    """

    GPT_4_5_PREVIEW = "gpt-4.5-preview"
    O3_MINI = "o3-mini"
    O1 = "o1"
    O1_MINI = "o1-mini"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4 = "gpt-4"
    GPT_3_5_TURBO = "gpt-3.5-turbo"

    @classmethod
    def get_provider(
        cls, model_name: Optional[Union[str, "AIModel"]] = None
    ) -> AIProvider:
        """
        Get the provider for a specific model.

        Args:
            model_name: The AIModel or model name string to get the provider for
        """
        if model_name is None:
            return AIProvider.OPENAI

        return AIProvider.OPENAI

    @classmethod
    def from_string(cls, model_name: str) -> "AIModel":
        """
        Convert a string representation to an AIModel enum value.

        Args:
            model_name: String name of the model

        """
        try:
            return cls(model_name)
        except ValueError:
            name_map = {
                "gpt-4.5-preview": cls.GPT_4_5_PREVIEW,
                "o3-mini": cls.O3_MINI,
                "o1": cls.O1,
                "o1-mini": cls.O1_MINI,
                "gpt-4o": cls.GPT_4O,
                "gpt-4o-mini": cls.GPT_4O_MINI,
                "gpt-4": cls.GPT_4,
                "gpt-4-turbo": cls.GPT_4_TURBO,
                "gpt-3.5-turbo": cls.GPT_3_5_TURBO,
            }

            if model_name in name_map:
                return name_map[model_name]

            raise ValueError(f"Unknown AI model: {model_name}")

    @classmethod
    def supports_structured_outputs(cls, model_name: Union[str, "AIModel"]) -> bool:
        """
        Check if a model supports structured outputs.

        Args:
            model_name: Name of the model to check (string or AIModel enum)
        """
        if isinstance(model_name, AIModel):
            model_str = model_name.value
        elif isinstance(model_name, Enum):
            try:
                model_str = model_name.value
            except AttributeError:
                model_str = str(model_name)
        else:
            model_str = str(model_name)

        return model_str in STRUCTURED_OUTPUT_MODELS

    @classmethod
    def get_token_param_name(cls, model_name: Union[str, "AIModel"]) -> str:
        """
        Determine which token parameter name to use based on the model.

        Args:
            model_name: Name of the model (string or AIModel enum)
        """
        log.debug(
            f"get_token_param_name called with: {model_name}, type: {type(model_name)}"
        )

        if isinstance(model_name, AIModel):
            model_str = model_name.value
            log.debug(f"Converted AIModel enum to string: {model_str}")
        elif isinstance(model_name, Enum):
            try:
                model_str = model_name.value
                log.debug(f"Converted enum to string: {model_str}")
            except AttributeError:
                model_str = str(model_name)
                log.debug(f"Used str() for enum: {model_str}")
        else:
            model_str = str(model_name)
            log.debug(f"Input is not an enum, using as string: {model_str}")

        if model_str in COMPLETION_TOKEN_MODELS:
            log.debug(f"Model {model_str} is in COMPLETION_TOKEN_MODELS list")
            return "max_completion_tokens"

        if any(
            o_model in model_str for o_model in ["o3-", "o1-", "gpt-4o"]
        ) or model_str in ["o1", "o3"]:
            log.debug(
                f"Model {model_str} is in the 'o' series, using max_completion_tokens"
            )
            return "max_completion_tokens"
        else:
            log.debug(f"Model {model_str} is not in the 'o' series, using max_tokens")
            return "max_tokens"

    @classmethod
    def get_unsupported_parameters(cls, model_name: Union[str, "AIModel"]) -> Set[str]:
        """
        Get the set of parameters that are unsupported by a specific model.

        Args:
            model_name: Name of the model (string or AIModel enum)
        """
        if isinstance(model_name, AIModel):
            model_str = model_name.value
        elif isinstance(model_name, Enum):
            try:
                model_str = model_name.value
            except AttributeError:
                model_str = str(model_name)
        else:
            model_str = str(model_name)

        if model_str in UNSUPPORTED_PARAMETERS:
            return UNSUPPORTED_PARAMETERS[model_str]

        if any(o_model in model_str for o_model in ["o3-", "o1-"]) or model_str in [
            "o1",
            "o3",
        ]:
            return {"temperature", "top_p", "parallel_tool_calls"}

        return set()
