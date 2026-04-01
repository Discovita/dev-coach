"""
services.ai.utils.openai

Utility functions for the OpenAI service implementation.
Each function is a standalone, testable unit responsible for one step of
the generate / call_sentinel pipeline.

Exports
-------
build_messages          Build the OpenAI chat message array.
structured_completion   Call beta.chat.completions.parse with the right params.
parse_coach_response    Extract a CoachChatResponse from a ParsedChatCompletion.
parse_sentinel_response Extract a SentinelChatResponse from a ParsedChatCompletion.
"""

from services.ai.utils.openai.build_messages import build_messages
from services.ai.utils.openai.parse_coach_response import parse_coach_response
from services.ai.utils.openai.parse_sentinel_response import parse_sentinel_response
from services.ai.utils.openai.structured_completion import structured_completion

__all__ = [
    "build_messages",
    "structured_completion",
    "parse_coach_response",
    "parse_sentinel_response",
]
