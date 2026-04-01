"""
Tests for services/ai/utils/openai/parse_sentinel_response.py
"""

from unittest.mock import MagicMock

from django.test import SimpleTestCase

from models.SentinelChatResponse import SentinelChatResponse
from services.ai.utils.openai.parse_sentinel_response import parse_sentinel_response


class MinimalSentinelResponseFormat(SentinelChatResponse):
    """Minimal SentinelChatResponse subclass used as response_format in tests."""
    pass


def _mock_completion(parsed_obj):
    """Return a mock ParsedChatCompletion with the given parsed object."""
    completion = MagicMock()
    completion.choices[0].message.parsed = parsed_obj
    return completion


class TestParseSentinelResponse(SimpleTestCase):
    """Unit tests for parse_sentinel_response."""

    def test_returns_sentinel_chat_response_instance(self):
        """parse_sentinel_response returns a SentinelChatResponse."""
        parsed_obj = MinimalSentinelResponseFormat()
        completion = _mock_completion(parsed_obj)
        result = parse_sentinel_response(completion, MinimalSentinelResponseFormat)
        self.assertIsInstance(result, SentinelChatResponse)

    def test_all_fields_none_when_no_actions(self):
        """All action fields are None when the parsed object has no actions."""
        parsed_obj = MinimalSentinelResponseFormat()
        completion = _mock_completion(parsed_obj)
        result = parse_sentinel_response(completion, MinimalSentinelResponseFormat)
        self.assertIsNone(result.add_user_note)
        self.assertIsNone(result.update_user_note)
        self.assertIsNone(result.delete_user_note)

    def test_extracts_from_choices_index_zero(self):
        """The parsed object is taken from choices[0].message.parsed."""
        parsed_obj = MinimalSentinelResponseFormat()
        completion = MagicMock()
        completion.choices[0].message.parsed = parsed_obj
        result = parse_sentinel_response(completion, MinimalSentinelResponseFormat)
        self.assertIsInstance(result, SentinelChatResponse)

    def test_accepts_empty_dict_parsed_object(self):
        """parse_sentinel_response handles an empty dict as the parsed value."""
        completion = _mock_completion({})
        result = parse_sentinel_response(completion, MinimalSentinelResponseFormat)
        self.assertIsInstance(result, SentinelChatResponse)

    def test_accepts_pydantic_model_as_parsed_object(self):
        """parse_sentinel_response handles a Pydantic model instance directly."""
        parsed_obj = MinimalSentinelResponseFormat()
        completion = _mock_completion(parsed_obj)
        result = parse_sentinel_response(completion, MinimalSentinelResponseFormat)
        self.assertIsInstance(result, SentinelChatResponse)
