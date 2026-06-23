"""
Tests for services/ai/utils/openai/structured_completion.py
"""

import json
from unittest.mock import MagicMock

from django.test import SimpleTestCase
from pydantic import BaseModel, ValidationError

from enums.ai import AIModel
from services.ai.utils.openai.structured_completion import structured_completion


def _mock_completion(parsed_obj=None):
    """Return a MagicMock that mimics completion.choices[0].message.parsed."""
    completion = MagicMock()
    completion.choices[0].message.parsed = parsed_obj or MagicMock()
    return completion


class _Probe(BaseModel):
    """Tiny schema standing in for a structured response_format."""

    message: str


def _validation_error_from_json(raw: str) -> ValidationError:
    """Produce the SAME ValidationError that .parse() raises on bad JSON, so its
    errors()[*]['input'] carries the full raw string the salvage path recovers."""
    try:
        _Probe.model_validate_json(raw)
    except ValidationError as e:
        return e
    raise AssertionError("expected the JSON to fail validation")


class TestStructuredCompletion(SimpleTestCase):
    """Unit tests for structured_completion."""

    def test_calls_beta_parse_endpoint(self):
        """structured_completion calls client.beta.chat.completions.parse."""
        client = MagicMock()
        client.beta.chat.completions.parse.return_value = _mock_completion()
        structured_completion(
            client=client,
            messages=[{"role": "system", "content": "test"}],
            model=AIModel.GPT_4O,
            response_format=MagicMock,
        )
        client.beta.chat.completions.parse.assert_called_once()

    def test_returns_completion_object(self):
        """structured_completion returns the value from the API call."""
        expected = _mock_completion()
        client = MagicMock()
        client.beta.chat.completions.parse.return_value = expected
        result = structured_completion(
            client=client,
            messages=[],
            model=AIModel.GPT_4O,
            response_format=MagicMock,
        )
        self.assertIs(result, expected)

    def test_passes_model_string_to_api(self):
        """The model string value (not the enum) is passed to the API."""
        client = MagicMock()
        client.beta.chat.completions.parse.return_value = _mock_completion()
        structured_completion(
            client=client,
            messages=[],
            model=AIModel.GPT_4O,
            response_format=MagicMock,
        )
        call_kwargs = client.beta.chat.completions.parse.call_args[1]
        self.assertEqual(call_kwargs["model"], AIModel.GPT_4O.value)

    def test_includes_temperature_for_gpt4o(self):
        """temperature is included in the request for GPT-4o."""
        client = MagicMock()
        client.beta.chat.completions.parse.return_value = _mock_completion()
        structured_completion(
            client=client,
            messages=[],
            model=AIModel.GPT_4O,
            response_format=MagicMock,
            temperature=0.5,
        )
        call_kwargs = client.beta.chat.completions.parse.call_args[1]
        self.assertIn("temperature", call_kwargs)
        self.assertEqual(call_kwargs["temperature"], 0.5)

    def test_omits_temperature_for_o1(self):
        """temperature is excluded for o1 models."""
        client = MagicMock()
        client.beta.chat.completions.parse.return_value = _mock_completion()
        structured_completion(
            client=client,
            messages=[],
            model=AIModel.O1,
            response_format=MagicMock,
            temperature=0.5,
        )
        call_kwargs = client.beta.chat.completions.parse.call_args[1]
        self.assertNotIn("temperature", call_kwargs)

    def test_omits_temperature_for_o3_mini(self):
        """temperature is excluded for o3-mini models."""
        client = MagicMock()
        client.beta.chat.completions.parse.return_value = _mock_completion()
        structured_completion(
            client=client,
            messages=[],
            model=AIModel.O3_MINI,
            response_format=MagicMock,
            temperature=0.7,
        )
        call_kwargs = client.beta.chat.completions.parse.call_args[1]
        self.assertNotIn("temperature", call_kwargs)

    def test_omits_temperature_for_o4_mini(self):
        """temperature is excluded for o4-mini models."""
        client = MagicMock()
        client.beta.chat.completions.parse.return_value = _mock_completion()
        structured_completion(
            client=client,
            messages=[],
            model=AIModel.O4_MINI,
            response_format=MagicMock,
            temperature=0.7,
        )
        call_kwargs = client.beta.chat.completions.parse.call_args[1]
        self.assertNotIn("temperature", call_kwargs)

    def test_uses_max_completion_tokens_for_gpt4o(self):
        """GPT-4o uses max_completion_tokens (not max_tokens)."""
        client = MagicMock()
        client.beta.chat.completions.parse.return_value = _mock_completion()
        structured_completion(
            client=client,
            messages=[],
            model=AIModel.GPT_4O,
            response_format=MagicMock,
        )
        call_kwargs = client.beta.chat.completions.parse.call_args[1]
        self.assertIn("max_completion_tokens", call_kwargs)
        self.assertNotIn("max_tokens", call_kwargs)

    def test_retries_with_swapped_token_param_on_conflict_error(self):
        """
        When the API raises an error mentioning both token param names,
        the function swaps the param and retries once.
        """
        second_response = _mock_completion()
        client = MagicMock()
        client.beta.chat.completions.parse.side_effect = [
            Exception("max_tokens and max_completion_tokens conflict"),
            second_response,
        ]
        result = structured_completion(
            client=client,
            messages=[],
            model=AIModel.GPT_4O,
            response_format=MagicMock,
        )
        self.assertEqual(client.beta.chat.completions.parse.call_count, 2)
        self.assertIs(result, second_response)

    def test_does_not_retry_on_unrelated_error(self):
        """Errors unrelated to token params are re-raised without retry."""
        client = MagicMock()
        client.beta.chat.completions.parse.side_effect = RuntimeError("network error")
        with self.assertRaises(RuntimeError):
            structured_completion(
                client=client,
                messages=[],
                model=AIModel.GPT_4O,
                response_format=MagicMock,
            )
        self.assertEqual(client.beta.chat.completions.parse.call_count, 1)

    def test_extra_kwargs_forwarded_to_api(self):
        """Caller kwargs (e.g. seed) are forwarded to the API call."""
        client = MagicMock()
        client.beta.chat.completions.parse.return_value = _mock_completion()
        structured_completion(
            client=client,
            messages=[],
            model=AIModel.GPT_4O,
            response_format=MagicMock,
            seed=42,
        )
        call_kwargs = client.beta.chat.completions.parse.call_args[1]
        self.assertEqual(call_kwargs["seed"], 42)

    def test_salvages_duplicated_json_object(self):
        """The duplicated-JSON glitch (a valid object emitted twice) is salvaged:
        the first object is decoded and re-validated, no retry, no raise."""
        obj = {"message": "Where did you grow up?"}
        duplicated = json.dumps(obj) + "\n" + json.dumps(obj)
        client = MagicMock()
        client.beta.chat.completions.parse.side_effect = _validation_error_from_json(
            duplicated
        )
        result = structured_completion(
            client=client,
            messages=[],
            model=AIModel.GPT_4O,
            response_format=_Probe,
        )
        self.assertEqual(client.beta.chat.completions.parse.call_count, 1)
        self.assertEqual(result.choices[0].message.parsed, _Probe(**obj))

    def test_salvages_single_object_with_trailing_garbage(self):
        """A valid first object followed by non-JSON trailing text is salvaged."""
        client = MagicMock()
        client.beta.chat.completions.parse.side_effect = _validation_error_from_json(
            '{"message":"hi"}\nthanks!'
        )
        result = structured_completion(
            client=client,
            messages=[],
            model=AIModel.GPT_4O,
            response_format=_Probe,
        )
        self.assertEqual(result.choices[0].message.parsed.message, "hi")

    def test_reraises_when_first_object_not_schema_valid(self):
        """If the first JSON object doesn't satisfy the schema, it's genuinely
        malformed — re-raise rather than salvage."""
        client = MagicMock()
        client.beta.chat.completions.parse.side_effect = _validation_error_from_json(
            '{"wrong_field":1}\n{"wrong_field":1}'
        )
        with self.assertRaises(ValidationError):
            structured_completion(
                client=client,
                messages=[],
                model=AIModel.GPT_4O,
                response_format=_Probe,
            )
