"""
Error handlers for the OpenAI chat completions.

This module contains functions that handle various errors that can occur
during chat completion API calls.
"""

from typing import Dict, Any
import logging

log = logging.getLogger(__name__)


def handle_token_parameter_error(
    self, error: ValueError, params: Dict[str, Any]
) -> Any:
    """
    Handle errors related to token parameters in chat completion requests.

    Parameters
    ----------
    self : The OpenAIService instance
    error : The error that occurred
    params : The parameters that were used in the request

    Returns
    -------
        The response from the API after fixing the token parameter
    """
    error_str = str(error)
    if "max_tokens" in error_str and "max_completion_tokens" in error_str:
        log.warning("Detected error related to token parameter. Attempting to fix...")

        if "max_tokens" in params:
            tokens_value = params.pop("max_tokens")
            params["max_completion_tokens"] = tokens_value
            log.debug(f"Retrying with max_completion_tokens={tokens_value}")
        elif "max_completion_tokens" in params:
            tokens_value = params.pop("max_completion_tokens")
            params["max_tokens"] = tokens_value
            log.debug(f"Retrying with max_tokens={tokens_value}")

        return self.client.chat.completions.create(**params)

    raise error
