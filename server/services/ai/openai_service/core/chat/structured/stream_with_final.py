"""
Streaming functionality for structured completions with final result.

This module provides the function for streaming structured chat completions
with access to both incremental updates and the final result.
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

from ....models.openai_compatibility import NotGiven, NOT_GIVEN
from ....models.response_types import ResponseFormatT
from .stream_completion import stream_structured_completion


def stream_structured_completion_with_final(
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
) -> Tuple[
    Generator[ParsedChatCompletion[ResponseFormatT], None, None],
    ParsedChatCompletion[ResponseFormatT],
]:
    """
    Stream a structured chat completion using the OpenAI API and return both the stream generator and final completion.
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
    A tuple containing:
        1. A generator that yields the partial completion objects
        2. The final complete response
    """
    stream_results = list(
        stream_structured_completion(
            self,
            messages=messages,
            model=model,
            response_format=response_format,
            frequency_penalty=frequency_penalty,
            logit_bias=logit_bias,
            logprobs=logprobs,
            max_tokens=max_tokens,
            max_completion_tokens=max_completion_tokens,
            n=n,
            presence_penalty=presence_penalty,
            seed=seed,
            stop=stop,
            temperature=temperature,
            tool_choice=tool_choice,
            tools=tools,
            top_logprobs=top_logprobs,
            top_p=top_p,
            user=user,
        )
    )

    final_completions = [res for res, is_final in stream_results if is_final]
    if not final_completions:
        raise ValueError("No final completion received from the stream")

    final_completion = final_completions[0]

    def completion_generator():
        for completion, _ in stream_results:
            if not isinstance(completion, ParsedChatCompletion):
                continue
            yield completion

    return completion_generator(), final_completion 