"""
Tests for services.action_handler.actions.persistent_components.start_break.

The handler opens a `Break` row and returns a SESSION_BREAK ComponentConfig
that renders the break card with an "I'm Ready" button bound to END_BREAK().
It is a user-button-only action: fired as the second action on the outro
video's Continue button, after ACKNOWLEDGE_SESSION_VIDEO.

Invariants tested here:
- One open break per user — overlap raises ValidationError
- session_key validated against the SESSIONS map
- session_key is the session being LEFT (not the user's current_phase session)
- Returned ComponentConfig propagates through apply_user_component_actions
  so PR 10's skip-LLM rule can fire on it
"""

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.actions.models import Action
from apps.coach.utils.apply_user_component_actions import (
    apply_user_component_actions,
)
from apps.coach_states.models import Break
from conftest import create_test_chat_message, create_test_user
from enums.action_type import ActionType
from enums.component_type import ComponentType
from enums.message_role import MessageRole
from models.components.ComponentConfig import ComponentAction, ComponentConfig
from services.action_handler.actions.persistent_components.start_break import (
    start_break,
)
from services.action_handler.models import StartBreakParams


class StartBreakActionTests(TestCase):
    """Tests for the start_break action handler."""

    def setUp(self):
        self.user = create_test_user()
        self.coach_state = self.user.coach_state
        self.coach_message = create_test_chat_message(
            self.user,
            role=MessageRole.COACH,
            content="Take a break before the next session.",
        )

    def test_start_break_creates_break_row_with_correct_triggered_by_session(
        self,
    ):
        """Should create exactly one Break row with `triggered_by_session`
        set to the session being left."""
        params = StartBreakParams(session_key="get_to_know_session")

        start_break(self.coach_state, params, self.coach_message)

        breaks = Break.objects.filter(user=self.user)
        self.assertEqual(breaks.count(), 1)
        self.assertEqual(breaks.first().triggered_by_session, "get_to_know_session")
        self.assertIsNone(breaks.first().ended_at)

    def test_start_break_returns_session_break_component_config(self):
        """Returned config must be a SESSION_BREAK with an 'I'm Ready' button
        whose action is END_BREAK (zero params)."""
        params = StartBreakParams(session_key="brainstorming_session")

        result = start_break(self.coach_state, params, self.coach_message)

        self.assertIsInstance(result, ComponentConfig)
        self.assertEqual(result.component_type, ComponentType.SESSION_BREAK.value)
        self.assertIsNotNone(result.buttons)
        self.assertEqual(len(result.buttons), 1)
        button = result.buttons[0]
        self.assertEqual(button.label, "I'm Ready")
        self.assertIsNotNone(button.actions)
        self.assertEqual(len(button.actions), 1)
        action = button.actions[0]
        self.assertEqual(action.action, ActionType.END_BREAK.value)
        self.assertEqual(action.params, {})

    def test_start_break_links_break_to_coach_message_when_provided(self):
        """The Break row's `coach_message` FK should point to the outro
        coach message that anchored the break card."""
        params = StartBreakParams(session_key="refinement_session")

        start_break(self.coach_state, params, self.coach_message)

        break_row = Break.objects.get(user=self.user)
        self.assertEqual(break_row.coach_message_id, self.coach_message.id)

    def test_start_break_raises_validation_error_when_open_break_exists_for_user(
        self,
    ):
        """Hard invariant: starting a second break while one is open raises
        ValidationError and does not create a duplicate row."""
        params = StartBreakParams(session_key="commitment_session")
        start_break(self.coach_state, params, self.coach_message)
        self.assertEqual(Break.objects.filter(user=self.user).count(), 1)

        with self.assertRaises(ValidationError):
            start_break(self.coach_state, params, self.coach_message)

        self.assertEqual(Break.objects.filter(user=self.user).count(), 1)

    def test_start_break_allowed_after_previous_break_closed(self):
        """Once `ended_at` is stamped, a new break can be opened."""
        from django.utils import timezone

        params_first = StartBreakParams(session_key="get_to_know_session")
        start_break(self.coach_state, params_first, self.coach_message)
        first_break = Break.objects.get(user=self.user)
        first_break.ended_at = timezone.now()
        first_break.save(update_fields=["ended_at"])

        params_second = StartBreakParams(session_key="brainstorming_session")
        result = start_break(self.coach_state, params_second, self.coach_message)

        self.assertIsInstance(result, ComponentConfig)
        self.assertEqual(Break.objects.filter(user=self.user).count(), 2)
        self.assertEqual(
            Break.objects.filter(user=self.user, ended_at__isnull=True).count(), 1
        )

    def test_start_break_isolates_per_user(self):
        """User A's open break must not block user B from opening one."""
        other_user = create_test_user(email="other@example.com")
        other_coach_state = other_user.coach_state
        other_coach_message = create_test_chat_message(
            other_user, role=MessageRole.COACH, content="Other user outro."
        )
        params = StartBreakParams(session_key="i_am_session")
        start_break(self.coach_state, params, self.coach_message)

        start_break(other_coach_state, params, other_coach_message)

        self.assertEqual(
            Break.objects.filter(user=self.user, ended_at__isnull=True).count(), 1
        )
        self.assertEqual(
            Break.objects.filter(user=other_user, ended_at__isnull=True).count(), 1
        )

    def test_start_break_raises_for_unknown_session_key(self):
        """Unknown session keys raise ValidationError and do not write state."""
        params = StartBreakParams(session_key="not_a_real_session")

        with self.assertRaises(ValidationError):
            start_break(self.coach_state, params, self.coach_message)

        self.assertFalse(Break.objects.filter(user=self.user).exists())
        self.assertFalse(
            Action.objects.filter(
                user=self.user, action_type=ActionType.START_BREAK.value
            ).exists()
        )

    def test_start_break_returned_component_triggers_skip_llm_rule_via_apply_user_component_actions(
        self,
    ):
        """Integration: dispatching START_BREAK through the user-component
        path must propagate the SESSION_BREAK ComponentConfig back to the
        orchestrator. PR 10 reads this value to skip the LLM call when set."""
        component_action = ComponentAction(
            action=ActionType.START_BREAK.value,
            params={"session_key": "get_to_know_session"},
        )

        component_config = apply_user_component_actions(
            self.coach_state, self.coach_message, [component_action]
        )

        self.assertIsInstance(component_config, ComponentConfig)
        self.assertEqual(
            component_config.component_type, ComponentType.SESSION_BREAK.value
        )
        self.assertTrue(
            Break.objects.filter(user=self.user, ended_at__isnull=True).exists()
        )
