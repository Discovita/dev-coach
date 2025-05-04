"""
Utility to format a generation prompt for a specific AI provider.
Used by prompt_manager and generation prompt logic.
"""

from pydantic import BaseModel
from enums.ai import AIProvider
from services.prompt_manager.models import PromptContext
from services.prompt_manager.utils import log_context_stats


def format_for_provider(
    prompt: str,
    prompt_context: PromptContext,
    provider: AIProvider,
    response_format: BaseModel,
):
    """Internal helper to apply provider-specific formatting to the prompt."""
    log_context_stats(prompt_context)
    if callable(getattr(prompt, "format", None)):
        # Anthropic: include response_format in the system message
        if provider == AIProvider.ANTHROPIC:
            prompt = prompt.format(**prompt_context.model_dump())
        # OpenAI: do not include response_format in the system message
        elif provider == AIProvider.OPENAI:
            prompt = prompt.format(**prompt_context.model_dump())
    if callable(getattr(prompt, "format", None)):
        prompt = prompt.format(**prompt_context.model_dump())

    # Step 3: Adjust response_format for each provider
    if provider == AIProvider.OPENAI:
        pass  # No additional formatting needed for OpenAI
    elif provider == AIProvider.ANTHROPIC:
        response_format_schema = response_format.model_json_schema()
        prompt += f"\n\nYour response must be in the form of a JSON object.\n{response_format_schema}"

    return prompt, response_format
