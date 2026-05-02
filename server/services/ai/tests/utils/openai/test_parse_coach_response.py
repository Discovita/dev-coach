"""
Tests for services/ai/utils/openai/parse_coach_response.py
"""

from unittest.mock import MagicMock

from django.test import SimpleTestCase

from models.CoachChatResponse import CoachChatResponse
from services.ai.utils.openai.parse_coach_response import parse_coach_response


class MinimalCoachResponseFormat(CoachChatResponse):
    """Minimal CoachChatResponse subclass used as response_format in tests."""
    pass


def _mock_completion(parsed_obj):
    """Return a mock ParsedChatCompletion with the given parsed object."""
    completion = MagicMock()
    completion.choices[0].message.parsed = parsed_obj
    return completion


class TestParseCoachResponse(SimpleTestCase):
    """Unit tests for parse_coach_response."""

    def test_returns_coach_chat_response_instance(self):
        """parse_coach_response returns a CoachChatResponse."""
        parsed_obj = MinimalCoachResponseFormat(message="Hello from coach.")
        completion = _mock_completion(parsed_obj)
        result = parse_coach_response(completion, MinimalCoachResponseFormat)
        self.assertIsInstance(result, CoachChatResponse)

    def test_message_content_preserved(self):
        """The message field from the parsed object is preserved."""
        parsed_obj = MinimalCoachResponseFormat(message="Keep going!")
        completion = _mock_completion(parsed_obj)
        result = parse_coach_response(completion, MinimalCoachResponseFormat)
        self.assertEqual(result.message, "Keep going!")

    def test_extracts_from_choices_index_zero(self):
        """The parsed object is taken from choices[0].message.parsed."""
        expected_msg = "Choice zero message."
        parsed_obj = MinimalCoachResponseFormat(message=expected_msg)
        completion = MagicMock()
        completion.choices[0].message.parsed = parsed_obj
        result = parse_coach_response(completion, MinimalCoachResponseFormat)
        self.assertEqual(result.message, expected_msg)

    def test_accepts_dict_parsed_object(self):
        """parse_coach_response handles a dict returned as the parsed value."""
        completion = _mock_completion({"message": "From dict."})
        result = parse_coach_response(completion, MinimalCoachResponseFormat)
        self.assertIsInstance(result, CoachChatResponse)
        self.assertEqual(result.message, "From dict.")

    def test_optional_action_fields_default_to_none(self):
        """Action fields not in the parsed object default to None."""
        parsed_obj = MinimalCoachResponseFormat(message="No actions.")
        completion = _mock_completion(parsed_obj)
        result = parse_coach_response(completion, MinimalCoachResponseFormat)
        self.assertIsNone(result.create_identity)
        self.assertIsNone(result.transition_phase)
