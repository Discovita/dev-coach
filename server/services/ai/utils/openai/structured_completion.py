"""
structured_completion

Calls the OpenAI beta.chat.completions.parse endpoint with structured output
support. Handles the two token-parameter families (max_tokens vs
max_completion_tokens) and silently strips temperature from o-series models
that do not accept it.

Retry behaviour:
    If the API returns an error mentioning both token parameter names, the
    function swaps the parameter and retries once. This guards against model
    family misclassification.
"""

import logging
from typing import List, Optional, Type

from openai.types.chat import ChatCompletionMessageParam, ParsedChatCompletion
from pydantic import BaseModel

from enums.ai import AIModel

log = logging.getLogger(__name__)

# o-series model name fragments that do not accept 'temperature' or 'top_p'.
_O_SERIES_TAGS = ("o1", "o3", "o4-mini")


def structured_completion(
    client,
    messages: List[ChatCompletionMessageParam],
    model: AIModel,
    response_format: Type[BaseModel],
    temperature: Optional[float] = 0.2,
    **kwargs,
) -> ParsedChatCompletion:
    """
    Call beta.chat.completions.parse and return the raw ParsedChatCompletion.

    Parameters
    ----------
    client : openai.OpenAI
        An initialised OpenAI client instance.
    messages : list of ChatCompletionMessageParam
        The message array to send (build with build_messages).
    model : AIModel
        The model enum value. Used to select the correct token parameter.
    response_format : Type[BaseModel]
        Pydantic model class the API should parse the response into.
    temperature : float, optional
        Sampling temperature. Omitted automatically for o-series models.
    **kwargs
        Additional parameters forwarded to the API (e.g. seed, top_p).
        Caller-supplied token parameters (max_tokens / max_completion_tokens)
        override the defaults derived from the model.

    Returns
    -------
    ParsedChatCompletion
        Raw completion. Access the parsed object via
        ``completion.choices[0].message.parsed``.

    Raises
    ------
    Exception
        Any OpenAI API exception that is not the known token-param conflict
        error is re-raised immediately without retry.
    """
    model_str = model.value
    token_param = AIModel.get_token_param_name(model)
    max_tokens = kwargs.pop(token_param, AIModel.get_default_token_limit(model))

    params = {
        "messages": messages,
        "model": model_str,
        "response_format": response_format,
        token_param: max_tokens,
    }

    # o-series models reject 'temperature'; skip it for those families.
    is_o_series = any(tag in model_str for tag in _O_SERIES_TAGS)
    if not is_o_series and temperature is not None:
        params["temperature"] = temperature

    for key, value in kwargs.items():
        if key not in params:
            params[key] = value

    log.debug(f"Sending structured completion request to OpenAI (model={model_str})")
    try:
        return client.beta.chat.completions.parse(**params)
    except Exception as e:
        error_str = str(e)
        if "max_tokens" in error_str and "max_completion_tokens" in error_str:
            alt_param = (
                "max_completion_tokens" if token_param == "max_tokens" else "max_tokens"
            )
            log.warning(f"Token param error — retrying with {alt_param}")
            params[alt_param] = params.pop(token_param)
            return client.beta.chat.completions.parse(**params)
        raise
