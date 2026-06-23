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

import json
import logging
from types import SimpleNamespace
from typing import List, Optional, Type

from openai.types.chat import ChatCompletionMessageParam, ParsedChatCompletion
from pydantic import BaseModel, ValidationError

from enums.ai import AIModel

log = logging.getLogger(__name__)

# Model name fragments for reasoning families that do not accept a custom
# 'temperature' / 'top_p' (o-series and the GPT-5 line).
_NO_TEMPERATURE_TAGS = ("o1", "o3", "o4-mini", "gpt-5")


def _recover_raw_content(exc: ValidationError) -> Optional[str]:
    """Pull the FULL raw model output out of a parse ValidationError.

    `.parse()` raises before returning, so the raw content is otherwise lost —
    but the structured errors retain the whole string (the exception's repr
    truncates it) under ``errors()[*]['input']``. Returns it, or None.
    """
    try:
        for err in exc.errors():
            candidate = err.get("input")
            if isinstance(candidate, str):
                return candidate
    except Exception:  # never let recovery mask the real error
        return None
    return None


def _salvage_structured_output(
    exc: Exception, response_format: Type[BaseModel], model_str: str
):
    """Recover from the duplicated-JSON glitch, returning a completion-shaped
    object or None if unrecoverable.

    Some models (observed intermittently on gpt-5.4, ~13% of action-bearing
    turns) emit the SAME valid JSON object TWICE, newline-separated:

        {"message":"...","update_asked_questions":{...}}
        {"message":"...","update_asked_questions":{...}}

    `.parse()` then fails with "trailing characters at line 2 column 1" and
    discards the result, even though the FIRST object is a complete, schema-valid
    answer (``finish_reason=stop`` — not a truncation). This is a model output
    quirk, not a real failure, so we decode just the first JSON value and
    re-validate it against the response_format. The returned shim only needs to
    satisfy ``completion.choices[0].message.parsed`` — the single field every
    caller reads.
    """
    if not isinstance(exc, ValidationError):
        return None
    raw = _recover_raw_content(exc)
    if not raw:
        return None
    try:
        obj, end = json.JSONDecoder().raw_decode(raw.strip())
    except (json.JSONDecodeError, ValueError):
        return None
    try:
        parsed = response_format.model_validate(obj)
    except ValidationError:
        return None  # first object isn't schema-valid — genuinely malformed

    trailing = raw.strip()[end:].strip()
    is_duplicate = False
    if trailing:
        try:
            dup, _ = json.JSONDecoder().raw_decode(trailing)
            is_duplicate = dup == obj
        except (json.JSONDecodeError, ValueError):
            is_duplicate = False

    log.warning(
        "RECOVERED_STRUCTURED_OUTPUT model=%s salvaged the first JSON object "
        "from a malformed structured response (duplicate=%s, trailing_len=%s). "
        "Output quirk, not a coaching failure.",
        model_str,
        is_duplicate,
        len(trailing),
    )
    message = SimpleNamespace(parsed=parsed, content=raw, refusal=None)
    choice = SimpleNamespace(message=message, finish_reason="stop", index=0)
    return SimpleNamespace(choices=[choice])


def _log_malformed_structured_output(exc: Exception, model_str: str) -> None:
    """Capture the FULL raw LLM output when structured-output parsing fails AND
    could not be salvaged.

    The complete content is recovered from the ValidationError (see
    ``_recover_raw_content``) and logged at ERROR with a stable, greppable marker
    (``MALFORMED_STRUCTURED_OUTPUT``) so a genuinely unrecoverable occurrence is
    fully diagnosable.
    """
    if not isinstance(exc, ValidationError):
        return

    raw = _recover_raw_content(exc)
    try:
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
                salvaged = _salvage_structured_output(
                    retry_exc, response_format, model_str
                )
                if salvaged is not None:
                    return salvaged
                _log_malformed_structured_output(retry_exc, model_str)
                raise
        # The duplicated-JSON glitch: the model emitted a valid object twice, so
        # .parse() raised on the trailing copy. Salvage the first (correct) one
        # rather than failing the turn.
        salvaged = _salvage_structured_output(e, response_format, model_str)
        if salvaged is not None:
            return salvaged
        # Otherwise capture the full raw output before re-raising so a genuinely
        # malformed response is diagnosable next time.
        _log_malformed_structured_output(e, model_str)
        raise
