from typing import Dict, Set, Union

from django.db import models


class AIProvider(models.TextChoices):
    """
    Enum representing different AI providers supported by the system.

    This enum is used to specify which AI provider to use when generating text.
    As new providers are added to the system, they should be added to this enum.
    """

    ANTHROPIC = "ANTHROPIC", "Anthropic"
    OPENAI = "OPENAI", "OpenAI"

    @classmethod
    def from_string(cls, provider_name: str) -> "AIProvider":
        """
        Convert a string representation to an AIProvider enum value.
        """
        name_map = {
            "anthropic": cls.ANTHROPIC,
            "claude": cls.ANTHROPIC,
            "openai": cls.OPENAI,
            "gpt": cls.OPENAI,
        }

        normalized_name = provider_name.lower()
        if normalized_name not in name_map:
            raise ValueError(f"Unknown AI provider: {provider_name}")

        return name_map[normalized_name]


class AIModel(models.TextChoices):
    """
    Enum representing different AI models supported by the system.
    """

    # Anthropic Claude models
    CLAUDE_3_7_SONNET = "claude-3-7-sonnet-latest", "Claude 3.7 Sonnet"
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-latest", "Claude 3.5 Sonnet"
    CLAUDE_3_5_HAIKU = "claude-3-5-haiku-latest", "Claude 3.5 Haiku"

    # OpenAI GPT-5 model (reasoning-capable; structured outputs supported)
    GPT_5_4 = "gpt-5.4", "GPT-5.4"

    # OpenAI GPT models
    GPT_4_1 = "gpt-4.1", "GPT-4.1"
    GPT_4_5_PREVIEW = "gpt-4.5-preview", "GPT-4.5 Preview"
    O1 = "o1", "o1"
    O1_MINI = "o1-mini", "O1 Mini"
    O3 = "o3", "o3"
    O3_MINI = "o3-mini", "O3 Mini"
    O4_MINI = "o4-mini", "O4 Mini"
    GPT_4O = "gpt-4o", "GPT 4o"
    GPT_4O_MINI = "gpt-4o-mini", "GPT 4o Mini"
    GPT_4_TURBO = "gpt-4-turbo", "GPT 4 Turbo"
    GPT_4 = "gpt-4", "GPT 4"
    GPT_3_5_TURBO = "gpt-3.5-turbo", "GPT 3.5 Turbo"

    @classmethod
    def get_provider(cls, model: "AIModel") -> AIProvider:
        """
        Get the provider for a specific model.
        """
        anthropic_models = [
            cls.CLAUDE_3_7_SONNET,
            cls.CLAUDE_3_5_SONNET,
            cls.CLAUDE_3_5_HAIKU,
        ]

        openai_models = [
            cls.GPT_5_4,
            cls.GPT_4_1,
            cls.GPT_4_5_PREVIEW,
            cls.O3_MINI,
            cls.O4_MINI,
            cls.O1,
            cls.O3,
            cls.O1_MINI,
            cls.GPT_4O,
            cls.GPT_4O_MINI,
            cls.GPT_4_TURBO,
            cls.GPT_4,
            cls.GPT_3_5_TURBO,
        ]

        if model in anthropic_models:
            return AIProvider.ANTHROPIC
        elif model in openai_models:
            return AIProvider.OPENAI
        else:
            raise ValueError(f"Unknown model provider for {model}")

    @classmethod
    def from_string(cls, model_name: str) -> "AIModel":
        """
        Convert a string representation to an AIModel enum value.
        """
        try:
            return cls(model_name)
        except ValueError:
            # Try some common aliases
            name_map = {
                "gpt-5.4": cls.GPT_5_4,
                "claude-3.7-sonnet": cls.CLAUDE_3_7_SONNET,
                "claude-3.5-sonnet": cls.CLAUDE_3_5_SONNET,
                "claude-3.5-haiku": cls.CLAUDE_3_5_HAIKU,
                "gpt-4.5-preview": cls.GPT_4_5_PREVIEW,
                "o3-mini": cls.O3_MINI,
                "o4-mini": cls.O4_MINI,
                "o1": cls.O1,
                "o3": cls.O3,
                "o1-mini": cls.O1_MINI,
                "gpt-4o": cls.GPT_4O,
                "gpt-4o-mini": cls.GPT_4O_MINI,
                "gpt-4": cls.GPT_4,
                "gpt-4-turbo": cls.GPT_4_TURBO,
                "gpt-3.5-turbo": cls.GPT_3_5_TURBO,
                "gpt-4.1": cls.GPT_4_1,
                "gpt-4.1-2025-04-14": cls.GPT_4_1,
            }

            if model_name in name_map:
                return name_map[model_name]

            raise ValueError(f"Unknown AI model: {model_name}")

    @classmethod
    def supports_structured_outputs(cls, model_name: str) -> bool:
        """
        Check if a model supports structured outputs.

        Since we only use predefined models from the enum and the API automatically
        uses the latest version, we can simply check if the model is in our list
        of supported models.
        See: STRUCTURED_OUTPUT_MODELS (module-level constant)
        """
        return model_name in STRUCTURED_OUTPUT_MODELS

    @classmethod
    def get_token_param_name(cls, model_name: Union[str, "AIModel"]) -> str:
        """
        Determine which token parameter name to use based on the model.
        See: COMPLETION_TOKEN_MODELS (module-level constant)
        """
        if isinstance(model_name, models.TextChoices):
            try:
                model_str = model_name.value
            except AttributeError:
                model_str = str(model_name)
        else:
            model_str = str(model_name)

        # Explicit check for 'o' series models
        if any(o_model in model_str for o_model in COMPLETION_TOKEN_MODELS):
            return "max_completion_tokens"
        else:
            return "max_tokens"

    @classmethod
    def get_default_token_limit(cls, model_name: Union[str, "AIModel"]) -> int:
        """
        Get the default token limit for a specific model.
        See: DEFAULT_TOKEN_LIMITS (module-level constant)
        """
        if hasattr(model_name, "value"):
            model_str = str(model_name.value)
        else:
            model_str = str(model_name)

        return DEFAULT_TOKEN_LIMITS.get(model_str, 1024)

    @classmethod
    def get_or_default(cls, model_name: str = None) -> "AIModel":
        """
        Get the AIModel from a string, or return the default model if not provided.
        This is useful for endpoints where the user may or may not specify a model.
        Default is the configured ``DEFAULT_AI_MODEL`` setting (env-driven),
        falling back to GPT_4O when unset. This lets a single setting flip the
        coach model per-environment without code changes.
        """
        if model_name:
            return cls.from_string(model_name)

        from django.conf import settings

        configured = getattr(settings, "DEFAULT_AI_MODEL", None)
        if configured:
            return cls.from_string(configured)
        return cls.GPT_4O


# -----------------------------------------------------------------------------
# Module-level constants for model capabilities and limits
# -----------------------------------------------------------------------------

# Set of model names that support structured outputs.
# Used in: AIModel.supports_structured_outputs
STRUCTURED_OUTPUT_MODELS: Set[str] = {
    "gpt-5.4",
    "gpt-4.1",
    "gpt-4.5-preview",
    "o1",
    "o3",
    "o3-mini",
    "o4-mini",
    "gpt-4o-mini",
    "gpt-4o",
}

# Set of model names that require max_completion_tokens parameter.
# Used in: AIModel.get_token_param_name
COMPLETION_TOKEN_MODELS: Set[str] = {
    "gpt-5",
    "gpt-4.1",
    "o1",
    "o1-mini",
    "o3",
    "o3-mini",
    "o4-mini",
    "gpt-4o",
    "gpt-4o-mini",
}

# Default token limits for each model.
# Used in: AIModel.get_default_token_limit
DEFAULT_TOKEN_LIMITS: Dict[str, int] = {
    # GPT-5.4 supports up to 128k output tokens (1.05M context window).
    "gpt-5.4": 128000,
    "gpt-4.1": 32768,
    "gpt-4.5-preview": 16384,
    "o3-mini": 100000,
    "o4-mini": 100000,
    "o1": 100000,
    "o3": 200000,
    "o1-mini": 65536,
    "gpt-4o": 16384,
    "gpt-4o-mini": 16384,
    "gpt-4-turbo": 4096,
    "gpt-4": 8192,
    "gpt-3.5-turbo": 4096,
    # Claude models
    "claude-3-7-sonnet-latest": 8192,
    "claude-3-5-sonnet-latest": 8192,
    "claude-3-5-haiku-latest": 8192,
}
