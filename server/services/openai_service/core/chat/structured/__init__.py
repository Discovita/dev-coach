"""
Structured completion functionality for OpenAIService.
"""

from .mixin import StructuredCompletionMixin
from .stream_completion import stream_structured_completion  
from .stream_with_final import stream_structured_completion_with_final

__all__ = [
    "StructuredCompletionMixin",
    "stream_structured_completion",
    "stream_structured_completion_with_final",
] 