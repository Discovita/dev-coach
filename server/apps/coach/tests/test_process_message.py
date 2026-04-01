"""
Tests for apps/coach/functions/public/process_message.py
"""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.coach.functions.public.process_message import process_message
from enums.ai import AIModel
from enums.message_role import MessageRole

PATCH_BASE = "apps.coach.functions.public.process_message"


def _make_coach_response(message="Coach reply", actions=None):
    """Helper: build a minimal mock CoachChatResponse."""
    response = MagicMock()
    response.message = message
    response.actions = actions or []
    return response


def _make_process_message_mocks():
    """Return a dict of all patches needed for a clean happy-path run."""
    mocks = {}
    mocks["ensure_initial_message_exists"] = MagicMock()
    mocks["add_chat_message"] = MagicMock(side_effect=[
        MagicMock(),  # user message
        MagicMock(),  # coach message
    ])
    mocks["coach_state"] = MagicMock()
    mocks["CoachState"] = MagicMock()
    mocks["CoachState"].objects.get.return_value = mocks["coach_state"]
    mocks["apply_user_component_actions"] = MagicMock()
    mocks["build_coach_prompt"] = MagicMock(return_value=("system_prompt", MagicMock()))
    mocks["get_recent_chat_messages_for_prompt"] = MagicMock(return_value=[])
    mocks["coach_response"] = _make_coach_response()
    mocks["generate_coach_ai_response"] = MagicMock(return_value=mocks["coach_response"])
    mocks["apply_coach_response_actions"] = MagicMock(return_value=(MagicMock(), None))
    mocks["build_coach_response_data"] = MagicMock(return_value={
        "message": "Coach reply",
        "final_prompt": "system_prompt",
    })
    return mocks


class TestProcessMessageHappyPath(SimpleTestCase):
    """Tests for the successful path through process_message."""

    def _run_with_patches(self, m, **overrides):
        """Apply all mocks as patches and run process_message."""
        merged = {**m, **overrides}
        user = MagicMock()
        user.id = "user-123"

        with (
            patch(f"{PATCH_BASE}.ensure_initial_message_exists", merged["ensure_initial_message_exists"]),
            patch(f"{PATCH_BASE}.add_chat_message", merged["add_chat_message"]),
            patch(f"{PATCH_BASE}.CoachState", merged["CoachState"]),
            patch(f"{PATCH_BASE}.apply_user_component_actions", merged["apply_user_component_actions"]),
            patch(f"{PATCH_BASE}.build_coach_prompt", merged["build_coach_prompt"]),
            patch(f"{PATCH_BASE}.get_recent_chat_messages_for_prompt", merged["get_recent_chat_messages_for_prompt"]),
            patch(f"{PATCH_BASE}.generate_coach_ai_response", merged["generate_coach_ai_response"]),
            patch(f"{PATCH_BASE}.apply_coach_response_actions", merged["apply_coach_response_actions"]),
            patch(f"{PATCH_BASE}.build_coach_response_data", merged["build_coach_response_data"]),
        ):
            return process_message(user, "Hello", None, AIModel.GPT_4O)

    def test_success_returns_true(self):
        """Success tuple starts with True."""
        m = _make_process_message_mocks()
        success, _, _ = self._run_with_patches(m)
        self.assertTrue(success)

    def test_success_returns_response_data(self):
        """Second element of the tuple is the response data dict."""
        m = _make_process_message_mocks()
        _, data, _ = self._run_with_patches(m)
        self.assertEqual(data["message"], "Coach reply")
        self.assertIn("final_prompt", data)

    def test_success_returns_none_as_error(self):
        """Third element of the tuple is None on success."""
        m = _make_process_message_mocks()
        _, _, error = self._run_with_patches(m)
        self.assertIsNone(error)

    def test_ensure_initial_message_called(self):
        """Step 1: ensure_initial_message_exists is always called."""
        m = _make_process_message_mocks()
        self._run_with_patches(m)
        m["ensure_initial_message_exists"].assert_called_once()

    def test_user_message_saved_to_chat_history(self):
        """Step 2: The user's message is saved with the USER role."""
        m = _make_process_message_mocks()
        user = MagicMock()
        user.id = "user-123"

        with (
            patch(f"{PATCH_BASE}.ensure_initial_message_exists"),
            patch(f"{PATCH_BASE}.add_chat_message", m["add_chat_message"]),
            patch(f"{PATCH_BASE}.CoachState", m["CoachState"]),
            patch(f"{PATCH_BASE}.apply_user_component_actions"),
            patch(f"{PATCH_BASE}.build_coach_prompt", m["build_coach_prompt"]),
            patch(f"{PATCH_BASE}.get_recent_chat_messages_for_prompt", m["get_recent_chat_messages_for_prompt"]),
            patch(f"{PATCH_BASE}.generate_coach_ai_response", m["generate_coach_ai_response"]),
            patch(f"{PATCH_BASE}.apply_coach_response_actions", m["apply_coach_response_actions"]),
            patch(f"{PATCH_BASE}.build_coach_response_data", m["build_coach_response_data"]),
        ):
            process_message(user, "Hello", None, AIModel.GPT_4O)

        first_call = m["add_chat_message"].call_args_list[0]
        self.assertEqual(first_call.args[1], "Hello")
        self.assertEqual(first_call.args[2], MessageRole.USER)

    def test_coach_reply_saved_to_chat_history(self):
        """Step 6: The coach's reply is saved with the COACH role."""
        m = _make_process_message_mocks()
        user = MagicMock()
        user.id = "user-123"

        with (
            patch(f"{PATCH_BASE}.ensure_initial_message_exists"),
            patch(f"{PATCH_BASE}.add_chat_message", m["add_chat_message"]),
            patch(f"{PATCH_BASE}.CoachState", m["CoachState"]),
            patch(f"{PATCH_BASE}.apply_user_component_actions"),
            patch(f"{PATCH_BASE}.build_coach_prompt", m["build_coach_prompt"]),
            patch(f"{PATCH_BASE}.get_recent_chat_messages_for_prompt", m["get_recent_chat_messages_for_prompt"]),
            patch(f"{PATCH_BASE}.generate_coach_ai_response", m["generate_coach_ai_response"]),
            patch(f"{PATCH_BASE}.apply_coach_response_actions", m["apply_coach_response_actions"]),
            patch(f"{PATCH_BASE}.build_coach_response_data", m["build_coach_response_data"]),
        ):
            process_message(user, "Hello", None, AIModel.GPT_4O)

        second_call = m["add_chat_message"].call_args_list[1]
        self.assertEqual(second_call.args[1], "Coach reply")
        self.assertEqual(second_call.args[2], MessageRole.COACH)


class TestProcessMessageErrorHandling(SimpleTestCase):
    """Tests for the error path through process_message."""

    def _run_with_error_in(self, step_name):
        """Patch a single step to raise and verify the error contract."""
        m = _make_process_message_mocks()
        m[step_name] = MagicMock(side_effect=RuntimeError("Something broke"))
        user = MagicMock()
        user.id = "user-123"

        with (
            patch(f"{PATCH_BASE}.ensure_initial_message_exists", m["ensure_initial_message_exists"]),
            patch(f"{PATCH_BASE}.add_chat_message", m["add_chat_message"]),
            patch(f"{PATCH_BASE}.CoachState", m["CoachState"]),
            patch(f"{PATCH_BASE}.apply_user_component_actions", m["apply_user_component_actions"]),
            patch(f"{PATCH_BASE}.build_coach_prompt", m["build_coach_prompt"]),
            patch(f"{PATCH_BASE}.get_recent_chat_messages_for_prompt", m["get_recent_chat_messages_for_prompt"]),
            patch(f"{PATCH_BASE}.generate_coach_ai_response", m["generate_coach_ai_response"]),
            patch(f"{PATCH_BASE}.apply_coach_response_actions", m["apply_coach_response_actions"]),
            patch(f"{PATCH_BASE}.build_coach_response_data", m["build_coach_response_data"]),
        ):
            return process_message(user, "Hello", None, AIModel.GPT_4O)

    def test_returns_false_on_exception(self):
        """Any exception causes the first element to be False."""
        success, _, _ = self._run_with_error_in("ensure_initial_message_exists")
        self.assertFalse(success)

    def test_returns_empty_dict_on_exception(self):
        """Any exception causes the second element to be an empty dict."""
        _, data, _ = self._run_with_error_in("generate_coach_ai_response")
        self.assertEqual(data, {})

    def test_returns_error_message_string_on_exception(self):
        """The third element is a non-empty error string on exception."""
        _, _, error = self._run_with_error_in("build_coach_prompt")
        self.assertIsInstance(error, str)
        self.assertIn("Something broke", error)

    def test_error_in_generate_caught(self):
        """An exception in generate_coach_ai_response is handled gracefully."""
        success, data, error = self._run_with_error_in("generate_coach_ai_response")
        self.assertFalse(success)
        self.assertEqual(data, {})
        self.assertIsNotNone(error)
