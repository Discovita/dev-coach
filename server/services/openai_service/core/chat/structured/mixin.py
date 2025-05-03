"""
Mixin for structured completion functionality in OpenAIService.
"""

from typing import (
    List,
    TypeVar,
    Type,
    Any,
    Optional,
    Dict,
    Union,
    Iterable,
    Generator,
    Tuple,
)
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionToolChoiceOptionParam,
    ChatCompletionToolParam,
    ParsedChatCompletion,
)

from pydantic import BaseModel
from ....models.openai_compatibility import NotGiven, NOT_GIVEN

ResponseFormatT = TypeVar("ResponseFormatT", bound=BaseModel)


class StructuredCompletionMixin:
    """
    Mixin providing structured completion functionality for OpenAIService.
    """

    def create_structured_chat_completion(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str,
        response_format: Type[ResponseFormatT],
        **kwargs: Any
    ) -> ParsedChatCompletion[ResponseFormatT]:
        """
        Creates a structured chat completion using the beta.chat.completions.parse endpoint.
        This method provides enhanced support for Pydantic models with automatic parsing.

        Parameters
        ----------
            messages : List of message objects to send to the API
            model : ID of the model to use
            response_format : A Pydantic model class that defines the structure of the response
            **kwargs : Additional parameters to pass to the API

        Returns
        -------
            A ParsedChatCompletion object containing the structured response.
            The parsed data can be accessed via completion.choices[0].message.parsed
        """
        from .structured_completion import (
            create_structured_chat_completion as create_structured_chat_completion_impl,
        )

        return create_structured_chat_completion_impl(
            self, messages, model, response_format, **kwargs
        )

    def stream_structured_completion(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str,
        response_format: Type[ResponseFormatT],
        **kwargs: Any
    ) -> Generator[Tuple[ParsedChatCompletion[ResponseFormatT], bool], None, None]:
        """
        Stream a structured chat completion using the beta.chat.completions.parse endpoint.
        This method provides enhanced support for Pydantic models with automatic parsing.

        Parameters
        ----------
            messages : List of message objects to send to the API
            model : ID of the model to use
            response_format : A Pydantic model class that defines the structure of the response
            **kwargs : Additional parameters to pass to the API

        Returns
        -------
            A generator that yields tuples containing:
                1. A parsed completion object
                2. A boolean indicating if this is the final completion

        Example
        -------
        >>> for parsed_data, is_final in helper.stream_structured_completion(
        ...     messages=messages,
        ...     model="gpt-4o",
        ...     response_format=MyModel
        ... ):
        ...     if is_final:
        ...         print("Final response:", parsed_data)
        ...     else:
        ...         print("Partial update:", parsed_data)
        """
        from .streaming import (
            stream_structured_completion as stream_structured_completion_impl,
        )

        return stream_structured_completion_impl(
            self, messages, model, response_format, **kwargs
        )

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
        Stream a structured chat completion using the OpenAI API and return both the stream and final completion.
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
            1. A generator that yields parsed completions as they become available
            2. The final complete response
        """
        from .streaming import (
            stream_structured_completion_with_final as stream_structured_completion_with_final_impl,
        )

        return stream_structured_completion_with_final_impl(
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
