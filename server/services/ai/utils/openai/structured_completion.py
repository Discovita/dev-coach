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
from pydantic import BaseModel, ValidationError

from enums.ai import AIModel

log = logging.getLogger(__name__)

# Model name fragments for reasoning families that do not accept a custom
# 'temperature' / 'top_p' (o-series and the GPT-5 line).
_NO_TEMPERATURE_TAGS = ("o1", "o3", "o4-mini", "gpt-5")


def _log_malformed_structured_output(exc: Exception, model_str: str) -> None:
    """Capture the FULL raw LLM output when structured-output parsing fails.

    The model very occasionally returns content that fails schema validation
    (e.g. the intermittent 'trailing characters' malformed-JSON glitch). When
    that happens `.parse()` raises a pydantic ``ValidationError`` and the raw
    model output is otherwise lost — the exception's string repr truncates it.

    The complete content is still available in ``ValidationError.errors()[*]
    ['input']`` (the repr truncates; the structured errors retain the whole
    string), so we recover and log it at ERROR with a stable, greppable marker
    (``MALFORMED_STRUCTURED_OUTPUT``). This is intentionally capture-only — it
    does not retry or recover — so the next occurrence is fully diagnosable.
    """
    if not isinstance(exc, ValidationError):
        return

    raw = None
    try:
        for err in exc.errors():
            candidate = err.get("input")
            if isinstance(candidate, str):
                raw = candidate
                break
        first_msg = exc.errors()[0].get("msg") if exc.errors() else str(exc)
    except Exception:  # never let diagnostic logging mask the real error
        first_msg = str(exc)

    log.error(
        "MALFORMED_STRUCTURED_OUTPUT model=%s error=%s raw_len=%s\n"
        "----- BEGIN RAW LLM OUTPUT -----\n%s\n----- END RAW LLM OUTPUT -----",
        model_str,
        first_msg,
        len(raw) if raw is not None else "unknown",
        raw if raw is not None else "<could not recover raw content from exception>",
    )


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

    # Reasoning families (o-series, GPT-5) reject 'temperature'; skip it.
    is_reasoning = any(tag in model_str for tag in _NO_TEMPERATURE_TAGS)
    if not is_reasoning and temperature is not None:
        params["temperature"] = temperature

    # GPT-5 accepts a 'reasoning_effort' control. Default it low for
    # latency-sensitive coach turns; a caller-supplied value wins.
    if "gpt-5" in model_str and "reasoning_effort" not in kwargs:
        params["reasoning_effort"] = "low"

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
            try:
                return client.beta.chat.completions.parse(**params)
            except Exception as retry_exc:
                _log_malformed_structured_output(retry_exc, model_str)
                raise
        # Capture the full raw LLM output on schema-validation failures (the
        # intermittent malformed-JSON glitch) before re-raising, so we can
        # diagnose it the next time it happens.
        _log_malformed_structured_output(e, model_str)
        raise
