"""
Tests for services/ai/openai_service.py

Covers the OpenAIService class itself: generate(), call_sentinel(),
get_provider_name(), and the AIServiceFactory.

Unit tests for the individual utility functions used internally are in:
    services/ai/tests/utils/openai/
"""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from enums.ai import AIModel, AIProvider
from models.CoachChatResponse import CoachChatResponse
from models.SentinelChatResponse import SentinelChatResponse
from services.ai.openai_service import OpenAIService


# ---------------------------------------------------------------------------
# Minimal Pydantic models used as response_format fixtures
# ---------------------------------------------------------------------------


class MinimalCoachResponse(CoachChatResponse):
    """
    Minimal subclass of CoachChatResponse used as a response_format in tests.
    All optional fields default to None; only 'message' is required.
    """
    pass


class MinimalSentinelResponse(SentinelChatResponse):
    """
    Minimal subclass of SentinelChatResponse used as a response_format in tests.
    All fields are optional.
    """
    pass


# ---------------------------------------------------------------------------
# Helper to build a mock ParsedChatCompletion
# ---------------------------------------------------------------------------

def _mock_completion(parsed_obj):
    """Return a MagicMock that mimics completion.choices[0].message.parsed."""
    completion = MagicMock()
    completion.choices[0].message.parsed = parsed_obj
    return completion


# ---------------------------------------------------------------------------
# Test: generate()
# ---------------------------------------------------------------------------

class TestGenerate(SimpleTestCase):
    """Tests for OpenAIService.generate()."""

    def _make_service(self, mock_client):
        """Construct an OpenAIService whose client is replaced by a mock."""
        service = OpenAIService.__new__(OpenAIService)
        service.client = mock_client
        return service

    def test_generate_returns_coach_chat_response(self):
        """generate() should return a CoachChatResponse on success."""
        parsed_obj = MinimalCoachResponse(message="Hello, I am your coach.")
        mock_client = MagicMock()
        mock_client.beta.chat.completions.parse.return_value = _mock_completion(parsed_obj)
        service = self._make_service(mock_client)

        result = service.generate(
            coach_prompt="You are a coach.",
            chat_history=[],
            response_format=MinimalCoachResponse,
            model=AIModel.GPT_4O,
        )

        self.assertIsInstance(result, CoachChatResponse)
        self.assertEqual(result.message, "Hello, I am your coach.")

    def test_generate_calls_parse_endpoint_once(self):
        """generate() should call beta.chat.completions.parse exactly once."""
        parsed_obj = MinimalCoachResponse(message="Response.")
        mock_client = MagicMock()
        mock_client.beta.chat.completions.parse.return_value = _mock_completion(parsed_obj)
        service = self._make_service(mock_client)

        service.generate(
            coach_prompt="Prompt",
            chat_history=[],
            response_format=MinimalCoachResponse,
            model=AIModel.GPT_4O,
        )

        mock_client.beta.chat.completions.parse.assert_called_once()

    def test_generate_passes_model_value_to_api(self):
        """generate() should pass the model string value to the API."""
        parsed_obj = MinimalCoachResponse(message="ok")
        mock_client = MagicMock()
        mock_client.beta.chat.completions.parse.return_value = _mock_completion(parsed_obj)
        service = self._make_service(mock_client)

        service.generate(
            coach_prompt="p",
            chat_history=[],
            response_format=MinimalCoachResponse,
            model=AIModel.GPT_4O,
        )

        call_kwargs = mock_client.beta.chat.completions.parse.call_args[1]
        self.assertEqual(call_kwargs["model"], AIModel.GPT_4O.value)

    def test_generate_omits_temperature_for_o_series(self):
        """generate() must not send temperature to o-series models."""
        parsed_obj = MinimalCoachResponse(message="ok")
        mock_client = MagicMock()
        mock_client.beta.chat.completions.parse.return_value = _mock_completion(parsed_obj)
        service = self._make_service(mock_client)

        service.generate(
            coach_prompt="p",
            chat_history=[],
            response_format=MinimalCoachResponse,
            model=AIModel.O3_MINI,
            temperature=0.5,
        )

        call_kwargs = mock_client.beta.chat.completions.parse.call_args[1]
        self.assertNotIn("temperature", call_kwargs)

    def test_generate_includes_temperature_for_gpt4o(self):
        """generate() should include temperature when using GPT-4o."""
        parsed_obj = MinimalCoachResponse(message="ok")
        mock_client = MagicMock()
        mock_client.beta.chat.completions.parse.return_value = _mock_completion(parsed_obj)
        service = self._make_service(mock_client)

        service.generate(
            coach_prompt="p",
            chat_history=[],
            response_format=MinimalCoachResponse,
            model=AIModel.GPT_4O,
            temperature=0.3,
        )

        call_kwargs = mock_client.beta.chat.completions.parse.call_args[1]
        self.assertIn("temperature", call_kwargs)
        self.assertEqual(call_kwargs["temperature"], 0.3)

    def test_generate_propagates_api_exception(self):
        """generate() should re-raise unexpected OpenAI API errors."""
        mock_client = MagicMock()
        mock_client.beta.chat.completions.parse.side_effect = RuntimeError("API down")
        service = self._make_service(mock_client)

        with self.assertRaises(RuntimeError):
            service.generate(
                coach_prompt="p",
                chat_history=[],
                response_format=MinimalCoachResponse,
                model=AIModel.GPT_4O,
            )


# ---------------------------------------------------------------------------
# Test: call_sentinel()
# ---------------------------------------------------------------------------

class TestCallSentinel(SimpleTestCase):
    """Tests for OpenAIService.call_sentinel()."""

    def _make_service(self, mock_client):
        service = OpenAIService.__new__(OpenAIService)
        service.client = mock_client
        return service

    def test_call_sentinel_returns_sentinel_chat_response(self):
        """call_sentinel() should return a SentinelChatResponse on success."""
        parsed_obj = MinimalSentinelResponse()
        mock_client = MagicMock()
        mock_client.beta.chat.completions.parse.return_value = _mock_completion(parsed_obj)
        service = self._make_service(mock_client)

        result = service.call_sentinel(
            sentinel_prompt="Extract notes.",
            response_format=MinimalSentinelResponse,
            model=AIModel.GPT_4O,
        )

        self.assertIsInstance(result, SentinelChatResponse)

    def test_call_sentinel_calls_parse_endpoint_once(self):
        """call_sentinel() should call beta.chat.completions.parse exactly once."""
        parsed_obj = MinimalSentinelResponse()
        mock_client = MagicMock()
        mock_client.beta.chat.completions.parse.return_value = _mock_completion(parsed_obj)
        service = self._make_service(mock_client)

        service.call_sentinel(
            sentinel_prompt="p",
            response_format=MinimalSentinelResponse,
            model=AIModel.GPT_4O,
        )

        mock_client.beta.chat.completions.parse.assert_called_once()

    def test_call_sentinel_omits_temperature_for_o1(self):
        """call_sentinel() must not send temperature to o1 models."""
        parsed_obj = MinimalSentinelResponse()
        mock_client = MagicMock()
        mock_client.beta.chat.completions.parse.return_value = _mock_completion(parsed_obj)
        service = self._make_service(mock_client)

        service.call_sentinel(
            sentinel_prompt="p",
            response_format=MinimalSentinelResponse,
            model=AIModel.O1,
            temperature=0.7,
        )

        call_kwargs = mock_client.beta.chat.completions.parse.call_args[1]
        self.assertNotIn("temperature", call_kwargs)


# ---------------------------------------------------------------------------
# Test: token parameter retry logic
# ---------------------------------------------------------------------------

class TestTokenParamRetry(SimpleTestCase):
    """
    Tests for the token parameter swap-and-retry behaviour in _structured_completion.

    The OpenAI API returns an error if the wrong token parameter is used
    (max_tokens vs max_completion_tokens). The service should detect this and
    retry once with the other parameter.
    """

    def _make_service(self, mock_client):
        service = OpenAIService.__new__(OpenAIService)
        service.client = mock_client
        return service

    def test_retries_with_swapped_token_param_on_token_error(self):
        """
        When the API raises an error mentioning both token param names, the
        service should swap the parameter and retry.
        """
        parsed_obj = MinimalCoachResponse(message="retry worked")
        mock_client = MagicMock()
        # First call raises the token error, second call succeeds
        mock_client.beta.chat.completions.parse.side_effect = [
            Exception("max_tokens and max_completion_tokens conflict"),
            _mock_completion(parsed_obj),
        ]
        service = self._make_service(mock_client)

        result = service.generate(
            coach_prompt="p",
            chat_history=[],
            response_format=MinimalCoachResponse,
            model=AIModel.GPT_4O,
        )

        self.assertEqual(mock_client.beta.chat.completions.parse.call_count, 2)
        self.assertEqual(result.message, "retry worked")

    def test_does_not_retry_on_unrelated_error(self):
        """
        An API error unrelated to token parameters should be re-raised immediately
        without a retry.
        """
        mock_client = MagicMock()
        mock_client.beta.chat.completions.parse.side_effect = RuntimeError("something else")
        service = self._make_service(mock_client)

        with self.assertRaises(RuntimeError):
            service.generate(
                coach_prompt="p",
                chat_history=[],
                response_format=MinimalCoachResponse,
                model=AIModel.GPT_4O,
            )

        self.assertEqual(mock_client.beta.chat.completions.parse.call_count, 1)


# ---------------------------------------------------------------------------
# Test: parse helpers (on AIService base)
# ---------------------------------------------------------------------------

class TestParseHelpers(SimpleTestCase):
    """
    Tests for AIService static parse helpers.
    These live on the base class but are tested via OpenAIService since it
    inherits them directly.
    """

    def test_extract_json_from_plain_string(self):
        """extract_json_from_response handles a raw JSON string."""
        from services.ai.base import AIService
        result = AIService.extract_json_from_response('{"message": "hello"}')
        self.assertEqual(result, {"message": "hello"})

    def test_extract_json_strips_markdown_fence(self):
        """extract_json_from_response strips ```json code fences."""
        from services.ai.base import AIService
        text = '```json\n{"message": "hello"}\n```'
        result = AIService.extract_json_from_response(text)
        self.assertEqual(result, {"message": "hello"})

    def test_extract_json_raises_on_no_json(self):
        """extract_json_from_response raises ValueError when no JSON found."""
        from services.ai.base import AIService
        with self.assertRaises(ValueError):
            AIService.extract_json_from_response("No JSON here at all.")

    def test_parse_response_from_pydantic_model(self):
        """parse_response accepts a Pydantic model instance directly."""
        from services.ai.base import AIService
        obj = MinimalCoachResponse(message="test message")
        result = AIService.parse_response(response=obj, dynamic_model=MinimalCoachResponse)
        self.assertIsInstance(result, CoachChatResponse)
        self.assertEqual(result.message, "test message")

    def test_parse_response_from_dict(self):
        """parse_response accepts a dict and validates it."""
        from services.ai.base import AIService
        result = AIService.parse_response(
            response={"message": "from dict"},
            dynamic_model=MinimalCoachResponse,
        )
        self.assertIsInstance(result, CoachChatResponse)
        self.assertEqual(result.message, "from dict")

    def test_parse_response_from_json_string(self):
        """parse_response extracts JSON from a string and validates it."""
        from services.ai.base import AIService
        result = AIService.parse_response(
            response='{"message": "from string"}',
            dynamic_model=MinimalCoachResponse,
        )
        self.assertIsInstance(result, CoachChatResponse)
        self.assertEqual(result.message, "from string")

    def test_parse_sentinel_response_from_pydantic_model(self):
        """parse_sentinel_response accepts a Pydantic model instance directly."""
        from services.ai.base import AIService
        obj = MinimalSentinelResponse()
        result = AIService.parse_sentinel_response(
            response=obj, dynamic_model=MinimalSentinelResponse
        )
        self.assertIsInstance(result, SentinelChatResponse)

    def test_parse_sentinel_response_from_dict(self):
        """parse_sentinel_response accepts an empty dict (all fields optional)."""
        from services.ai.base import AIService
        result = AIService.parse_sentinel_response(
            response={}, dynamic_model=MinimalSentinelResponse
        )
        self.assertIsInstance(result, SentinelChatResponse)


# ---------------------------------------------------------------------------
# Test: AIServiceFactory
# ---------------------------------------------------------------------------

class TestAIServiceFactory(SimpleTestCase):
    """Tests for AIServiceFactory.create()."""

    @patch("services.ai.ai_service_factory.os.getenv", return_value="test-api-key")
    @patch("services.ai.openai_service.OpenAI")
    def test_create_openai_model_returns_openai_service(self, mock_openai_cls, _mock_env):
        """create() with an OpenAI model should return an OpenAIService instance."""
        from services.ai.ai_service_factory import AIServiceFactory
        service = AIServiceFactory.create(AIModel.GPT_4O)
        self.assertIsInstance(service, OpenAIService)

    @patch("services.ai.ai_service_factory.os.getenv", return_value=None)
    def test_create_raises_when_api_key_missing(self, _mock_env):
        """create() should raise ValueError when OPENAI_API_KEY is not set."""
        from services.ai.ai_service_factory import AIServiceFactory
        with self.assertRaises(ValueError):
            AIServiceFactory.create(AIModel.GPT_4O)

    def test_create_raises_for_anthropic_model(self):
        """create() should raise NotImplementedError for Anthropic models."""
        from services.ai.ai_service_factory import AIServiceFactory
        with self.assertRaises(NotImplementedError):
            AIServiceFactory.create(AIModel.CLAUDE_3_5_SONNET)

    @patch("services.ai.ai_service_factory.os.getenv", return_value="test-api-key")
    @patch("services.ai.openai_service.OpenAI")
    def test_created_service_implements_ai_service_interface(self, mock_openai_cls, _mock_env):
        """The returned service must satisfy the AIService interface."""
        from services.ai.ai_service_factory import AIServiceFactory
        from services.ai.base import AIService
        service = AIServiceFactory.create(AIModel.GPT_4O)
        self.assertIsInstance(service, AIService)

    @patch("services.ai.ai_service_factory.os.getenv", return_value="test-api-key")
    @patch("services.ai.openai_service.OpenAI")
    def test_get_provider_name_returns_openai(self, mock_openai_cls, _mock_env):
        """get_provider_name() on the created service must return AIProvider.OPENAI."""
        from services.ai.ai_service_factory import AIServiceFactory
        service = AIServiceFactory.create(AIModel.GPT_4O)
        self.assertEqual(service.get_provider_name(), AIProvider.OPENAI)
