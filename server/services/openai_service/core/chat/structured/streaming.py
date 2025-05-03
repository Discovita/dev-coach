"""
Streaming functionality for structured completions.

This module provides functions for streaming structured chat completions
using the OpenAI API, with Pydantic model parsing support.

This file re-exports functions from stream_completion.py and stream_with_final.py
for backward compatibility.
"""

# Re-export functions from specialized modules
from .stream_completion import stream_structured_completion
from .stream_with_final import stream_structured_completion_with_final

__all__ = ["stream_structured_completion", "stream_structured_completion_with_final"] 