"""
Tests for apps/coach/functions/public/process_message.py

Covers the orchestrator's null-message contract and skip-LLM-on-component
rule alongside the existing happy-path and error-path assertions.
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
        MagicMock(),  # user message (when message is not None)
        MagicMock(),  # coach message
    ])
    mocks["coach_state"] = MagicMock()
    mocks["CoachState"] = MagicMock()
    mocks["CoachState"].objects.get.return_value = mocks["coach_state"]
    # Default to no user-action component → LLM path runs.
    mocks["apply_user_component_actions"] = MagicMock(return_value=None)
    mocks["build_coach_prompt"] = MagicMock(return_value=("system_prompt", MagicMock()))
    mocks["get_recent_chat_messages_for_prompt"] = MagicMock(return_value=[])
    mocks["coach_response"] = _make_coach_response()
    mocks["generate_coach_ai_response"] = MagicMock(return_value=mocks["coach_response"])
    mocks["apply_coach_response_actions"] = MagicMock(return_value=(MagicMock(), None))
    mocks["build_coach_response_data"] = MagicMock(return_value={
        "message": "Coach reply",
        "final_prompt": "system_prompt",
        "on_break": False,
    })
    # Mock the Break-linkage lookup the orchestrator does after the
    # skip-LLM rule creates a SESSION_BREAK coach message. Default to "no
    # open break to link" so tests that don't care don't trip over ORM
    # calls against MagicMock users.
    mocks["Break"] = MagicMock()
    mocks["Break"].objects.filter.return_value.order_by.return_value.first.return_value = None
    return mocks


def _patches(m):
    """Build the standard list of patch context managers for one run."""
    return [
        patch(f"{PATCH_BASE}.ensure_initial_message_exists", m["ensure_initial_message_exists"]),
        patch(f"{PATCH_BASE}.add_chat_message", m["add_chat_message"]),
        patch(f"{PATCH_BASE}.CoachState", m["CoachState"]),
        patch(f"{PATCH_BASE}.apply_user_component_actions", m["apply_user_component_actions"]),
        patch(f"{PATCH_BASE}.build_coach_prompt", m["build_coach_prompt"]),
        patch(f"{PATCH_BASE}.get_recent_chat_messages_for_prompt", m["get_recent_chat_messages_for_prompt"]),
        patch(f"{PATCH_BASE}.generate_coach_ai_response", m["generate_coach_ai_response"]),
        patch(f"{PATCH_BASE}.apply_coach_response_actions", m["apply_coach_response_actions"]),
        patch(f"{PATCH_BASE}.build_coach_response_data", m["build_coach_response_data"]),
        patch(f"{PATCH_BASE}.Break", m["Break"]),
    ]


def _make_user():
    user = MagicMock()
    user.id = "user-123"
    # MagicMock auto-chains, but force a concrete bool for the on_break read
    # so the orchestrator's `user.breaks.filter(...).exists()` returns a real
    # value the build_coach_response_data mock can ignore safely.
    user.breaks.filter.return_value.exists.return_value = False
    return user


class TestProcessMessageHappyPath(SimpleTestCase):
    """Tests for the successful path through process_message."""

    def _run_with_patches(self, m, **overrides):
        """Apply all mocks as patches and run process_message."""
        merged = {**m, **overrides}
        user = _make_user()
        p = _patches(merged)

        with p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9]:
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
        user = _make_user()

        with (
            patch(f"{PATCH_BASE}.ensure_initial_message_exists"),
            patch(f"{PATCH_BASE}.add_chat_message", m["add_chat_message"]),
            patch(f"{PATCH_BASE}.CoachState", m["CoachState"]),
            patch(f"{PATCH_BASE}.apply_user_component_actions", m["apply_user_component_actions"]),
            patch(f"{PATCH_BASE}.build_coach_prompt", m["build_coach_prompt"]),
            patch(f"{PATCH_BASE}.get_recent_chat_messages_for_prompt", m["get_recent_chat_messages_for_prompt"]),
            patch(f"{PATCH_BASE}.generate_coach_ai_response", m["generate_coach_ai_response"]),
            patch(f"{PATCH_BASE}.apply_coach_response_actions", m["apply_coach_response_actions"]),
            patch(f"{PATCH_BASE}.build_coach_response_data", m["build_coach_response_data"]),
            patch(f"{PATCH_BASE}.Break", m["Break"]),
        ):
            process_message(user, "Hello", None, AIModel.GPT_4O)

        first_call = m["add_chat_message"].call_args_list[0]
        self.assertEqual(first_call.args[1], "Hello")
        self.assertEqual(first_call.args[2], MessageRole.USER)

    def test_coach_reply_saved_to_chat_history(self):
        """Step 6: The coach's reply is saved with the COACH role."""
        m = _make_process_message_mocks()
        user = _make_user()

        with (
            patch(f"{PATCH_BASE}.ensure_initial_message_exists"),
            patch(f"{PATCH_BASE}.add_chat_message", m["add_chat_message"]),
            patch(f"{PATCH_BASE}.CoachState", m["CoachState"]),
            patch(f"{PATCH_BASE}.apply_user_component_actions", m["apply_user_component_actions"]),
            patch(f"{PATCH_BASE}.build_coach_prompt", m["build_coach_prompt"]),
            patch(f"{PATCH_BASE}.get_recent_chat_messages_for_prompt", m["get_recent_chat_messages_for_prompt"]),
            patch(f"{PATCH_BASE}.generate_coach_ai_response", m["generate_coach_ai_response"]),
            patch(f"{PATCH_BASE}.apply_coach_response_actions", m["apply_coach_response_actions"]),
            patch(f"{PATCH_BASE}.build_coach_response_data", m["build_coach_response_data"]),
            patch(f"{PATCH_BASE}.Break", m["Break"]),
        ):
            process_message(user, "Hello", None, AIModel.GPT_4O)

        second_call = m["add_chat_message"].call_args_list[1]
        self.assertEqual(second_call.args[1], "Coach reply")
        self.assertEqual(second_call.args[2], MessageRole.COACH)


class TestProcessMessageNullMessageContract(SimpleTestCase):
    """Tests for PR 10's null-message contract."""

    def _run(self, m, message):
        user = _make_user()
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
            patch(f"{PATCH_BASE}.Break", m["Break"]),
        ):
            return process_message(user, message, None, AIModel.GPT_4O)

    def test_message_none_does_not_save_user_chatmessage(self):
        """With message=None, no USER ChatMessage is saved — only the coach reply."""
        m = _make_process_message_mocks()
        # Only one add_chat_message call (the coach reply) — provide a single side_effect.
        m["add_chat_message"] = MagicMock(side_effect=[MagicMock()])

        self._run(m, message=None)

        # Exactly one call, and it must be the COACH message.
        self.assertEqual(len(m["add_chat_message"].call_args_list), 1)
        only_call = m["add_chat_message"].call_args_list[0]
        self.assertEqual(only_call.args[2], MessageRole.COACH)

    def test_message_none_still_applies_user_actions(self):
        """With message=None, apply_user_component_actions still runs."""
        m = _make_process_message_mocks()
        m["add_chat_message"] = MagicMock(side_effect=[MagicMock()])

        actions_payload = [{"action": "acknowledge_session_video", "params": {"video_key": "welcome_session_intro"}}]
        user = _make_user()
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
            patch(f"{PATCH_BASE}.Break", m["Break"]),
        ):
            process_message(user, None, actions_payload, AIModel.GPT_4O)

        m["apply_user_component_actions"].assert_called_once()
        # apply_user_component_actions(coach_state, user_chat_message, request_component_actions)
        call_args = m["apply_user_component_actions"].call_args
        self.assertIsNone(call_args.args[1])  # user_chat_message is None
        self.assertEqual(call_args.args[2], actions_payload)

    def test_message_empty_string_saves_user_chatmessage_with_empty_content(self):
        """`message=""` is a real (empty) user message and IS saved."""
        m = _make_process_message_mocks()

        self._run(m, message="")

        first_call = m["add_chat_message"].call_args_list[0]
        self.assertEqual(first_call.args[1], "")
        self.assertEqual(first_call.args[2], MessageRole.USER)

    def test_message_string_saves_user_chatmessage_with_content(self):
        """A plain message string is saved as the USER message with its content."""
        m = _make_process_message_mocks()

        self._run(m, message="Tell me a joke")

        first_call = m["add_chat_message"].call_args_list[0]
        self.assertEqual(first_call.args[1], "Tell me a joke")
        self.assertEqual(first_call.args[2], MessageRole.USER)


class TestProcessMessageSkipLlmRule(SimpleTestCase):
    """Tests for PR 10's skip-LLM-on-component rule."""

    def _run(self, m, message="Hello"):
        user = _make_user()
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
            patch(f"{PATCH_BASE}.Break", m["Break"]),
        ):
            return process_message(user, message, None, AIModel.GPT_4O)

    def test_skip_llm_when_user_action_returns_component_config(self):
        """A user action returning a ComponentConfig short-circuits the LLM call."""
        m = _make_process_message_mocks()
        component = MagicMock()
        component.component_type = "session_break"
        component.model_dump.return_value = {"component_type": "session_break"}
        m["apply_user_component_actions"] = MagicMock(return_value=component)

        success, _data, _err = self._run(m)

        self.assertTrue(success)
        m["generate_coach_ai_response"].assert_not_called()
        m["build_coach_prompt"].assert_not_called()
        # The returned component should be passed through to the builder.
        builder_kwargs = m["build_coach_response_data"].call_args.kwargs
        self.assertIs(builder_kwargs["component_config"], component)

    def test_llm_called_when_no_component_config_returned(self):
        """When user actions return None, the LLM is invoked as usual."""
        m = _make_process_message_mocks()
        m["apply_user_component_actions"] = MagicMock(return_value=None)

        self._run(m)

        m["generate_coach_ai_response"].assert_called_once()
        m["build_coach_prompt"].assert_called_once()

    def test_existing_process_message_flows_unchanged(self):
        """Regression: with no actions and a plain message, the LLM path runs end-to-end."""
        m = _make_process_message_mocks()

        success, data, error = self._run(m, message="What should I do?")

        self.assertTrue(success)
        self.assertIsNone(error)
        # User message saved → LLM called → coach reply saved → coach actions applied.
        m["apply_user_component_actions"].assert_called_once()
        m["build_coach_prompt"].assert_called_once()
        m["generate_coach_ai_response"].assert_called_once()
        m["apply_coach_response_actions"].assert_called_once()
        self.assertEqual(data["message"], "Coach reply")


class TestProcessMessageErrorHandling(SimpleTestCase):
    """Tests for the error path through process_message."""

    def _run_with_error_in(self, step_name):
        """Patch a single step to raise and verify the error contract."""
        m = _make_process_message_mocks()
        m[step_name] = MagicMock(side_effect=RuntimeError("Something broke"))
        user = _make_user()

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
            patch(f"{PATCH_BASE}.Break", m["Break"]),
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


# ---------------------------------------------------------------------------
# Break.coach_message retroactive linkage (skip-LLM SESSION_BREAK path)
# ---------------------------------------------------------------------------
#
# START_BREAK runs BEFORE the orchestrator's skip-LLM rule creates the
# SESSION_BREAK coach message, so `Break.coach_message` is None at the
# moment the Break row is created. The orchestrator must link them after
# the message exists so END_BREAK can find the SESSION_BREAK card to
# mutate to the closed state.


class TestProcessMessageBreakLinkage:
    """Pytest-style integration test: real DB models, only
    `apply_user_component_actions` mocked to drive the skip-LLM path
    with a SESSION_BREAK component."""

    def test_links_open_break_to_new_session_break_message(self, db):
        from unittest.mock import patch

        from apps.chat_messages.models import ChatMessage
        from apps.coach_states.models import Break
        from apps.users.models import User
        from enums.component_type import ComponentType
        from models.components.ComponentConfig import ComponentConfig

        user = User.objects.create_user(
            email="break_linkage@test.com", password="testpass"
        )
        # Open Break with no coach_message — the historic state right
        # after START_BREAK fires, before this fix linked them up.
        open_break = Break.objects.create(
            user=user,
            triggered_by_session="get_to_know_session",
        )
        assert open_break.coach_message_id is None

        # Drive the skip-LLM rule: have user-actions return a SESSION_BREAK.
        session_break = ComponentConfig(
            component_type=ComponentType.SESSION_BREAK.value
        )
        with patch(
            f"{PATCH_BASE}.apply_user_component_actions",
            return_value=session_break,
        ):
            success, _data, _err = process_message(
                user, None, [{"action": "start_break", "params": {}}], AIModel.GPT_4O
            )

        assert success is True

        # Break now references the just-created SESSION_BREAK coach message.
        open_break.refresh_from_db()
        assert open_break.coach_message_id is not None

        # And that message IS the SESSION_BREAK card.
        coach_msg: ChatMessage = open_break.coach_message
        assert coach_msg.role == MessageRole.COACH
        assert (
            coach_msg.component_config["component_type"]
            == ComponentType.SESSION_BREAK.value
        )

    def test_does_not_clobber_existing_coach_message_fk(self, db):
        """If Break.coach_message is already set (newer flows where
        START_BREAK already had a message to link to), the orchestrator
        leaves the FK alone — guarded by `coach_message_id is None`."""
        from unittest.mock import patch

        from apps.chat_messages.models import ChatMessage
        from apps.coach_states.models import Break
        from apps.users.models import User
        from enums.component_type import ComponentType
        from models.components.ComponentConfig import ComponentConfig

        user = User.objects.create_user(
            email="break_no_clobber@test.com", password="testpass"
        )
        # Pre-existing coach message that the Break already links to.
        existing_msg = ChatMessage.objects.create(
            user=user, role=MessageRole.COACH, content="seeded"
        )
        open_break = Break.objects.create(
            user=user,
            triggered_by_session="brainstorming_session",
            coach_message=existing_msg,
        )

        session_break = ComponentConfig(
            component_type=ComponentType.SESSION_BREAK.value
        )
        with patch(
            f"{PATCH_BASE}.apply_user_component_actions",
            return_value=session_break,
        ):
            process_message(user, None, [{"action": "start_break", "params": {}}], AIModel.GPT_4O)

        open_break.refresh_from_db()
        assert open_break.coach_message_id == existing_msg.id

    def test_does_not_link_for_non_session_break_skip_llm_components(self, db):
        """SESSION_VIDEO (END_BREAK's intro emit) hits the same skip-LLM
        branch — but the orchestrator should NOT touch any Break row for
        that case. Only SESSION_BREAK triggers the linkage."""
        from unittest.mock import patch

        from apps.coach_states.models import Break
        from apps.users.models import User
        from enums.component_type import ComponentType
        from models.components.ComponentConfig import ComponentConfig

        user = User.objects.create_user(
            email="break_video_skip@test.com", password="testpass"
        )
        # Open break (e.g., user just clicked I'm Ready, but for this test
        # the skip-LLM component is SESSION_VIDEO, not SESSION_BREAK).
        open_break = Break.objects.create(
            user=user,
            triggered_by_session="get_to_know_session",
        )

        session_video = ComponentConfig(
            component_type=ComponentType.SESSION_VIDEO.value,
            video_key="brainstorming_session_intro",
        )
        with patch(
            f"{PATCH_BASE}.apply_user_component_actions",
            return_value=session_video,
        ):
            process_message(user, None, [{"action": "end_break", "params": {}}], AIModel.GPT_4O)

        open_break.refresh_from_db()
        # FK untouched — Break.coach_message is still None.
        assert open_break.coach_message_id is None
