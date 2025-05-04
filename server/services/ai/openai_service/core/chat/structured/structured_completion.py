"""
Structured output functionality for the OpenAI API.

This module provides functions for creating structured chat completions
using the OpenAI API, with Pydantic model parsing support.
"""

from typing import List, Optional, Dict, Union, Iterable, Type
from openai.types.chat import (
    ParsedChatCompletion,
    ChatCompletionMessageParam,
    ChatCompletionToolChoiceOptionParam,
    ChatCompletionToolParam,
)
import logging
from ....models.openai_compatibility import NotGiven, NOT_GIVEN
from ....utils.model_utils import get_token_param_name, filter_unsupported_parameters
from ....models.response_types import ResponseFormatT

log = logging.getLogger(__name__)

try:
    USE_AI_MODEL_ENUM = True
    log.debug("Using AIModel enum for model-specific logic")
except ImportError:
    USE_AI_MODEL_ENUM = False
    log.debug("AIModel enum not available, falling back to hardcoded model checks")


def create_structured_chat_completion(
    self,
    messages: List[ChatCompletionMessageParam],
    model: str,
    response_format: Type[ResponseFormatT],
    frequency_penalty: Optional[float] | NotGiven = NOT_GIVEN,
    logit_bias: Optional[Dict[str, int]] | NotGiven = NOT_GIVEN,
    logprobs: Optional[bool] | NotGiven = NOT_GIVEN,
    max_tokens: Optional[int] | None = 4096,
    max_completion_tokens: Optional[int] | None = None,
    n: Optional[int] | None = 1,
    presence_penalty: Optional[float] | NotGiven = NOT_GIVEN,
    seed: Optional[int] | NotGiven = NOT_GIVEN,
    stop: Union[Optional[str], List[str]] | NotGiven = NOT_GIVEN,
    temperature: Optional[float] | None = 0.7,
    tool_choice: ChatCompletionToolChoiceOptionParam | NotGiven = NOT_GIVEN,
    tools: Iterable[ChatCompletionToolParam] | NotGiven = NOT_GIVEN,
    top_logprobs: Optional[int] | NotGiven = NOT_GIVEN,
    top_p: Optional[float] | NotGiven = NOT_GIVEN,
    user: str | NotGiven = NOT_GIVEN,
) -> ParsedChatCompletion[ResponseFormatT]:
    """
    Creates a structured chat completion using the beta.chat.completions.parse endpoint.
    This method provides enhanced support for Pydantic models with automatic parsing.

    Parameters
    ----------
    messages: List of message objects to send to the API.
    model: ID of the model to use.
    response_format: A Pydantic model class that defines the structure of the response.
    frequency_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far.
    logit_bias: Modify the likelihood of specified tokens appearing in the completion.
    logprobs: Whether to return log probabilities of the output tokens or not.
    max_tokens: The maximum number of tokens that can be generated in the chat completion.
    Note: Not supported by o-series models.
    max_completion_tokens: The maximum number of tokens to generate in the chat completion.
    Required for o-series models (o1, o3-mini).
    n: How many chat completion choices to generate for each input message.
    presence_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens
    based on whether they appear in the text so far.
    seed: If specified, our system will make a best effort to sample deterministically.
    stop: Up to 4 sequences where the API will stop generating further tokens.
    temperature: What sampling temperature to use, between 0 and 2.
    tool_choice: Controls which (if any) function is called by the model.
    tools: A list of tools the model may call.
    top_logprobs: An integer between 0 and 20 specifying the number of most likely tokens
    to return at each token position.
    top_p: An alternative to sampling with temperature, called nucleus sampling.
    user: A unique identifier representing your end-user.

    Returns
    -------
    ParsedChatCompletion[ResponseFormatT]
        A ParsedChatCompletion object containing the structured response.
        The parsed data can be accessed via completion.choices[0].message.parsed
    """
    log.debug("create_structured_chat_completion")

    token_param_name = get_token_param_name(model)
    tokens_value = (
        max_completion_tokens
        if token_param_name == "max_completion_tokens"
        and max_completion_tokens is not None
        else max_tokens
    )
    log.debug(f"Using {token_param_name}={tokens_value} for model: {model}")

    parse_params = {
        "messages": messages,
        "model": model,
        "response_format": response_format,
        "frequency_penalty": frequency_penalty,
        "logit_bias": logit_bias,
        "logprobs": logprobs,
        "n": n,
        "presence_penalty": presence_penalty,
        "seed": seed,
        "stop": stop,
        "temperature": temperature,
        "tool_choice": tool_choice,
        "tools": tools,
        "top_logprobs": top_logprobs,
        "top_p": top_p,
        "user": user,
        token_param_name: tokens_value,
    }

    parse_params = {k: v for k, v in parse_params.items() if v is not None}
    parse_params = {k: v for k, v in parse_params.items() if v is not NOT_GIVEN}
    parse_params = filter_unsupported_parameters(parse_params, model)
    log.debug("Sending structured completion request to OpenAI API")

    try:
        return self.client.beta.chat.completions.parse(**parse_params)
    except Exception as e:
        log.error(f"Error in beta parse endpoint: {e}")

        error_str = str(e)
        if "max_tokens" in error_str and "max_completion_tokens" in error_str:
            log.warning(
                "Detected error related to token parameter in beta parse. Attempting to fix..."
            )

            other_param = (
                "max_completion_tokens"
                if token_param_name == "max_tokens"
                else "max_tokens"
            )
            if token_param_name in parse_params:
                tokens_value = parse_params.pop(token_param_name)
                parse_params[other_param] = tokens_value
                log.debug(f"Retrying beta parse with {other_param}={tokens_value}")
                return self.client.beta.chat.completions.parse(**parse_params)

        raise
