"""
Model feature support collections.

This module contains the collections of model features supported
by different AI models, such as structured outputs and token parameters.
"""

from typing import Dict, Set

import logging

log = logging.getLogger(__name__)

STRUCTURED_OUTPUT_MODELS: Set[str] = {
    "gpt-4.5-preview",
    "o3-mini",
    "o1",
    "gpt-4o-mini",
    "gpt-4o",
}

COMPLETION_TOKEN_MODELS: Set[str] = {
    "o3-mini",
    "o1",
    "o1-mini",
    "gpt-4o",
    "gpt-4o-mini",
}

UNSUPPORTED_PARAMETERS: Dict[str, Set[str]] = {
    "o3-mini": {"temperature", "top_p", "parallel_tool_calls"},
    "o1": {"temperature", "top_p", "parallel_tool_calls"},
    "o1-mini": {"temperature", "top_p", "parallel_tool_calls"},
}
