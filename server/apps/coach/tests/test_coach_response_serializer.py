"""
Tests for CoachResponseSerializer.

Locks the shapes that `build_coach_response_data` actually emits — most
importantly the **skip-LLM rule** payload where `message` and
`final_prompt` are both empty strings (the component carries the turn,
not text). Without `allow_blank=True` on both fields, the view's
`serializer.is_valid(raise_exception=True)` returned a 400 to the
client when START_BREAK or END_BREAK fired in production.
"""

from django.test import TestCase

from apps.coach.serializers import CoachResponseSerializer
from enums.component_type import ComponentType


class CoachResponseSerializerTests(TestCase):
    """CoachResponseSerializer validation tests."""

    def test_accepts_llm_path_payload(self):
        """Normal LLM path: both message and final_prompt populated."""
        data = {
            "message": "Hi, I'm Leigh-Ann.",
            "final_prompt": "System prompt...",
            "on_break": False,
        }
        ser = CoachResponseSerializer(data=data)
        self.assertTrue(ser.is_valid(), msg=ser.errors)

    def test_accepts_skip_llm_payload_with_session_break(self):
        """Skip-LLM rule (START_BREAK): message + final_prompt are blank,
        component carries the turn. This was the bug that 400-ed the
        get_to_know_session outro Continue in live testing."""
        data = {
            "message": "",
            "final_prompt": "",
            "on_break": True,
            "component": {
                "component_type": ComponentType.SESSION_BREAK.value,
                "buttons": [
                    {
                        "label": "I'm Ready",
                        "actions": [{"action": "end_break", "params": {}}],
                    }
                ],
            },
        }
        ser = CoachResponseSerializer(data=data)
        self.assertTrue(ser.is_valid(), msg=ser.errors)

    def test_accepts_skip_llm_payload_with_session_video(self):
        """Skip-LLM rule (END_BREAK emitting intro): same shape, SESSION_VIDEO
        component instead of SESSION_BREAK."""
        data = {
            "message": "",
            "final_prompt": "",
            "on_break": False,
            "component": {
                "component_type": ComponentType.SESSION_VIDEO.value,
                "video_key": "brainstorming_session_intro",
            },
        }
        ser = CoachResponseSerializer(data=data)
        self.assertTrue(ser.is_valid(), msg=ser.errors)

    def test_message_required(self):
        """Omitting message entirely is still invalid — empty is fine,
        absent is not (matches the contract — build_coach_response_data
        always sets it, even to '')."""
        data = {"final_prompt": "", "on_break": False}
        ser = CoachResponseSerializer(data=data)
        self.assertFalse(ser.is_valid())
        self.assertIn("message", ser.errors)

    def test_final_prompt_required(self):
        """Same as message — always set by build_coach_response_data."""
        data = {"message": "", "on_break": False}
        ser = CoachResponseSerializer(data=data)
        self.assertFalse(ser.is_valid())
        self.assertIn("final_prompt", ser.errors)

    def test_on_break_required(self):
        """on_break drives the composer-disable rule — must always be present."""
        data = {"message": "", "final_prompt": ""}
        ser = CoachResponseSerializer(data=data)
        self.assertFalse(ser.is_valid())
        self.assertIn("on_break", ser.errors)
