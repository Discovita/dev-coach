"""
Streaming functionality for structured completions.

This module provides the core streaming function for structured chat completions
using the OpenAI API, with Pydantic model parsing support.
"""

from typing import List, Optional, Dict, Union, Iterable, Type, Generator, Tuple
from openai.types.chat import (
    ParsedChatCompletion,
    ChatCompletionMessageParam,
    ChatCompletionToolChoiceOptionParam,
    ChatCompletionToolParam,
)
import logging

log = logging.getLogger(__name__)

from ....models.openai_compatibility import NotGiven, NOT_GIVEN, Stream
from ....utils.model_utils import get_token_param_name, filter_unsupported_parameters
from ....models.response_types import ResponseFormatT


def stream_structured_completion(
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
) -> Generator[Tuple[ParsedChatCompletion[ResponseFormatT], bool], None, None]:
    """
    Stream a structured chat completion using the OpenAI API.
    This method provides enhanced support for Pydantic models with automatic parsing.

    Parameters
    ----------
    messages : List of message objects to send to the API
    model : ID of the model to use
    response_format : A Pydantic model class that defines the structure of the response
    frequency_penalty : Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency
    logit_bias : Modify the likelihood of specified tokens appearing in the completion
    logprobs : Whether to return log probabilities of the output tokens
    max_tokens : Maximum number of tokens that can be generated (not supported by o-series models)
    max_completion_tokens : Maximum number of tokens to generate (required for o-series models)
    n : Number of chat completion choices to generate
    presence_penalty : Number between -2.0 and 2.0. Positive values penalize new tokens based on presence
    seed : If specified, system will make best effort to sample deterministically
    stop : Up to 4 sequences where the API will stop generating further tokens
    temperature : What sampling temperature to use, between 0 and 2
    tool_choice : Controls which (if any) function is called by the model
    tools : List of tools the model may call
    top_logprobs : Number of most likely tokens to return at each position (0-20)
    top_p : Alternative to sampling with temperature, called nucleus sampling
    user : Unique identifier representing your end-user

    Returns
    -------
    Generator[Tuple[ParsedChatCompletion[ResponseFormatT], bool], None, None]
        A generator that yields tuples of (parsed_completion, is_final).
        is_final is True for the final complete response, False for incremental updates.
    """
    log.debug("stream_structured_completion")

    token_param_name = get_token_param_name(model)
    tokens_value = (
        max_completion_tokens
        if token_param_name == "max_completion_tokens"
        and max_completion_tokens is not None
        else max_tokens
    )
    log.debug(f"Using {token_param_name}={tokens_value} for model: {model}")

    stream_params = {
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

    stream_params = {k: v for k, v in stream_params.items() if v is not None}
    stream_params = {k: v for k, v in stream_params.items() if v is not NOT_GIVEN}
    stream_params = filter_unsupported_parameters(stream_params, model)
    log.debug("Starting structured completion stream")

    try:
        with self.client.beta.chat.completions.stream(**stream_params) as stream:
            for event in stream:
                if event.type == "content.delta" and event.parsed is not None:
                    yield event.parsed, False
                elif event.type == "content.done":
                    final_completion = stream.get_final_completion()
                    yield final_completion, True
                elif event.type == "error":
                    log.error("Stream error: %s", event.error)
                    raise Exception(f"Stream error: {event.error}")

    except Exception as e:
        log.error(f"Error in stream: {e}")

        error_str = str(e)
        if "max_tokens" in error_str and "max_completion_tokens" in error_str:
            log.warning(
                "Detected error related to token parameter. Attempting to fix..."
            )

            other_param = (
                "max_completion_tokens"
                if token_param_name == "max_tokens"
                else "max_tokens"
            )
            if token_param_name in stream_params:
                tokens_value = stream_params.pop(token_param_name)
                stream_params[other_param] = tokens_value
                log.debug(f"Retrying stream with {other_param}={tokens_value}")

                with self.client.beta.chat.completions.stream(
                    **stream_params
                ) as stream:
                    for event in stream:
                        if event.type == "content.delta" and event.parsed is not None:
                            yield event.parsed, False
                        elif event.type == "content.done":
                            final_completion = stream.get_final_completion()
                            yield final_completion, True
                        elif event.type == "error":
                            log.error("Stream error: %s", event.error)
                            raise Exception(f"Stream error: {event.error}")

        raise 