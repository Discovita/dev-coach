"""
Mixin for generic chat completion functionality in OpenAIService.

This mixin provides the core chat completion functionality for the OpenAI API,
including support for text generation, streaming, and basic parameter handling.
"""

from typing import List, Optional, Dict, Any, Union, Iterable, Type
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessageParam,
    ChatCompletionToolChoiceOptionParam,
    ChatCompletionToolParam,
    ChatCompletionStreamOptionsParam,
    ChatCompletionModality,
)
from pydantic import BaseModel
from ....models.openai_compatibility import NotGiven, NOT_GIVEN, Stream

import logging

log = logging.getLogger(__name__)


class GenericChatCompletionMixin:
    """
    Mixin providing generic chat completion functionality for OpenAIService.
    This includes basic text generation, streaming, and parameter handling.
    """

    def create_chat_completion(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str = "gpt-4-turbo-preview",
        stream: bool = False,
        json_mode: bool = False,
        max_tokens: Optional[int] | None = 4096,
        max_completion_tokens: Optional[int] | None = None,
        temperature: Optional[float] | None = 0.7,
        n: Optional[int] | None = 1,
        frequency_penalty: Optional[float] | NotGiven = NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | NotGiven = NOT_GIVEN,
        logprobs: Optional[bool] | NotGiven = NOT_GIVEN,
        presence_penalty: Optional[float] | NotGiven = NOT_GIVEN,
        response_format: Union[Dict[str, Any], Type[BaseModel], NotGiven] = NOT_GIVEN,
        seed: Optional[int] | NotGiven = NOT_GIVEN,
        stop: Union[Optional[str], List[str]] | NotGiven = NOT_GIVEN,
        tool_choice: ChatCompletionToolChoiceOptionParam | NotGiven = NOT_GIVEN,
        tools: Iterable[ChatCompletionToolParam] | NotGiven = NOT_GIVEN,
        top_logprobs: Optional[int] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        stream_options: Optional[ChatCompletionStreamOptionsParam] = None,
        modalities: Optional[List[ChatCompletionModality]] = None,
    ) -> Union[Dict[str, Any], str, ChatCompletion, Stream[ChatCompletionChunk]]:
        """
        Create a chat completion using OpenAI's API.

        Parameters
        ----------
        messages : The list of messages for the conversation
        model : The OpenAI model to use (default: "gpt-4-turbo-preview")
        stream : Whether to stream the response (default: False)
        json_mode : Whether to force the model to return valid JSON (default: False)
        max_tokens : Maximum tokens in the response for applicable models (default: 4096)
        max_completion_tokens : Maximum tokens in the response for O-series models (default: None)
        temperature : Controls randomness in the response (default: 0.7)
        n : Number of completions to generate (default: 1)
        frequency_penalty : Controls repetition penalty (default: NOT_GIVEN)
        logit_bias : Modifies token probabilities (default: NOT_GIVEN)
        logprobs : Whether to return log probabilities (default: NOT_GIVEN)
        presence_penalty : Penalty for new tokens (default: NOT_GIVEN)
        response_format : Controls response format (default: NOT_GIVEN)
        seed : Seed for deterministic outputs (default: NOT_GIVEN)
        stop : Token(s) to stop generation (default: NOT_GIVEN)
        tool_choice : Controls tool selection (default: NOT_GIVEN)
        tools : Tools to make available (default: NOT_GIVEN)
        top_logprobs : Number of most likely tokens to return (default: NOT_GIVEN)
        top_p : Controls diversity via nucleus sampling (default: NOT_GIVEN)
        user : User identifier (default: NOT_GIVEN)
        stream_options : Additional streaming options (default: None)
        modalities : Modalities of the input (default: None)

        Returns
        -------
        Union[Dict[str, Any], str, ChatCompletion, Stream[ChatCompletionChunk]]
            The model's response in the appropriate format
        """
        from .generic_completion import create_generic_chat_completion

        return create_generic_chat_completion(
            self,
            messages=messages,
            model=model,
            stream=stream,
            json_mode=json_mode,
            max_tokens=max_tokens,
            max_completion_tokens=max_completion_tokens,
            temperature=temperature,
            n=n,
            frequency_penalty=frequency_penalty,
            logit_bias=logit_bias,
            logprobs=logprobs,
            presence_penalty=presence_penalty,
            response_format=response_format,
            seed=seed,
            stop=stop,
            tool_choice=tool_choice,
            tools=tools,
            top_logprobs=top_logprobs,
            top_p=top_p,
            user=user,
            stream_options=stream_options,
            modalities=modalities,
        )
