"""
Implementation of generic chat completion functionality.
"""

import json
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
import logging
from ....models.openai_compatibility import NotGiven, NOT_GIVEN, Stream
from ....utils.model_utils import get_token_param_name, filter_unsupported_parameters

log = logging.getLogger(__name__)


def create_generic_chat_completion(
    self,
    messages: List[ChatCompletionMessageParam],
    model: str,
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
    self : The OpenAIService instance
    messages : The list of messages for the conversation
    model : The OpenAI model to use
    stream : Whether to stream the response
    json_mode : Whether to force the model to return valid JSON
    max_tokens : Maximum tokens in the response for applicable models
    max_completion_tokens : Maximum tokens in the response for O-series models
    temperature : Controls randomness in the response
    n : Number of completions to generate
    frequency_penalty : Controls repetition penalty
    logit_bias : Modifies token probabilities
    logprobs : Whether to return log probabilities
    presence_penalty : Penalty for new tokens
    response_format : Controls response format
    seed : Seed for deterministic outputs
    stop : Token(s) to stop generation
    tool_choice : Controls tool selection
    tools : Tools to make available
    top_logprobs : Number of most likely tokens to return
    top_p : Controls diversity via nucleus sampling
    user : User identifier
    stream_options : Additional streaming options
    modalities : Modalities of the input

    Returns
    -------
    Union[Dict[str, Any], str, ChatCompletion, Stream[ChatCompletionChunk]]
        The model's response in the appropriate format
    """
    token_param_name = get_token_param_name(model)

    if (
        token_param_name == "max_completion_tokens"
        and max_completion_tokens is not None
    ):
        token_value = max_completion_tokens
    else:
        token_value = max_tokens

    prepared_response_format = NOT_GIVEN

    if json_mode:
        prepared_response_format = {"type": "json_object"}
        log.debug("Using JSON mode for response format")
    elif isinstance(response_format, dict):
        prepared_response_format = response_format
        log.debug(f"Using dictionary response format: {response_format}")
    elif isinstance(response_format, type) and issubclass(response_format, BaseModel):
        schema = response_format.model_json_schema()
        prepared_response_format = {"type": "json_object", "schema": schema}
        log.debug(f"Using Pydantic model schema for response format: {schema}")

    params = {
        "model": model,
        "messages": messages,
        token_param_name: token_value,
        "temperature": temperature,
        "n": n,
        "stream": stream,
        "response_format": prepared_response_format,
        "frequency_penalty": frequency_penalty,
        "logit_bias": logit_bias,
        "logprobs": logprobs,
        "presence_penalty": presence_penalty,
        "seed": seed,
        "stop": stop,
        "tool_choice": tool_choice,
        "tools": tools,
        "top_logprobs": top_logprobs,
        "top_p": top_p,
        "user": user,
        "stream_options": stream_options,
        "modalities": modalities,
    }

    params = filter_unsupported_parameters(params, model)

    clean_params = {k: v for k, v in params.items() if v is not NOT_GIVEN}

    try:
        log.debug(f"Sending chat completion request to model {model}")
        response = self.client.chat.completions.create(**clean_params)

        return process_chat_completion_response(
            response, stream, prepared_response_format
        )
    except ValueError as e:
        from .error_handlers import handle_token_parameter_error

        return handle_token_parameter_error(self, e, clean_params)
    except Exception as e:
        log.error(f"Error in chat completion request: {str(e)}")
        raise


def process_chat_completion_response(
    response, stream: bool, prepared_response_format: Any
) -> Union[Dict[str, Any], str, ChatCompletion]:
    """
    Process the response from the OpenAI API based on the requested format.

    Parameters
    ----------
    response : The raw response from the API
    stream : Whether the response is a stream
    prepared_response_format : The prepared response format specification

    Returns
    -------
    Union[Dict[str, Any], str, ChatCompletion]
        The processed response in the appropriate format
    """
    if stream:
        log.debug("Returning stream response")
        return response
    elif (
        prepared_response_format is not NOT_GIVEN
        and isinstance(prepared_response_format, dict)
        and prepared_response_format.get("type") == "json_object"
    ):
        try:
            content = response.choices[0].message.content
            if content is not None:
                json_data = json.loads(content)
                log.debug("Successfully parsed JSON response")
                return json_data
            else:
                log.warning("Received None content in JSON mode response")
                return {}
        except json.JSONDecodeError:
            log.error("Failed to decode JSON response")
            return response.choices[0].message.content or ""
        except Exception as e:
            log.error(f"Error processing JSON response: {str(e)}")
            return response
    else:
        text_content = response.choices[0].message.content
        if text_content is None:
            log.warning("Received None content in text response")
            return ""
        return text_content
