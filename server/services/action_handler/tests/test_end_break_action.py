"""
Tests for services.action_handler.actions.end_break.

This PR ships the **basic close**: stamp `ended_at` on the user's single
open Break and write an Action audit row. The handler returns None — the
intro-emission side effect (returning a SESSION_VIDEO ComponentConfig for
the next session's intro when current_phase is at a session boundary with
an unacked intro) is added in PR 14.

PR 7's START_BREAK enforces at-most-one-open-break-per-user, so the
lookup here can safely use `.filter().first()` and treat the no-open-break
case as a no-op (defensive against duplicate clicks).
"""

from django.test import TestCase
from django.utils import timezone

from apps.actions.models import Action
from apps.coach_states.models import Break
from conftest import create_test_chat_message, create_test_user
from enums.action_type import ActionType
from enums.message_role import MessageRole
from services.action_handler.actions.end_break import end_break
from services.action_handler.models import EndBreakParams


class EndBreakActionTests(TestCase):
    """Tests for the end_break action handler (basic close — PR 8)."""

    def setUp(self):
        self.user = create_test_user()
        self.coach_state = self.user.coach_state
        self.coach_message = create_test_chat_message(
            self.user,
            role=MessageRole.COACH,
            content="Break card with I'm Ready button.",
        )
        self.params = EndBreakParams()

    def _open_break(self, user=None, triggered_by_session="get_to_know_session"):
        return Break.objects.create(
            user=user or self.user,
            triggered_by_session=triggered_by_session,
        )

    def test_end_break_stamps_ended_at_on_open_break(self):
        """The user's single open break should have ended_at set after dispatch."""
        open_break = self._open_break()
        self.assertIsNone(open_break.ended_at)

        end_break(self.coach_state, self.params, self.coach_message)

        open_break.refresh_from_db()
        self.assertIsNotNone(open_break.ended_at)
        self.assertTrue(open_break.ended_at <= timezone.now())

        action = Action.objects.filter(
            user=self.user, action_type=ActionType.END_BREAK.value
        ).first()
        self.assertIsNotNone(action)
        self.assertIn(str(open_break.id), action.result_summary)

    def test_end_break_no_op_when_no_open_break(self):
        """No open break → no exception, no Break mutation, no Action row."""
        result = end_break(self.coach_state, self.params, self.coach_message)

        self.assertIsNone(result)
        self.assertFalse(Break.objects.filter(user=self.user).exists())
        self.assertFalse(
            Action.objects.filter(
                user=self.user, action_type=ActionType.END_BREAK.value
            ).exists()
        )

    def test_end_break_only_closes_current_users_break(self):
        """Other users' open breaks must stay open."""
        my_break = self._open_break()
        other_user = create_test_user(email="other@example.com")
        other_break = self._open_break(user=other_user)

        end_break(self.coach_state, self.params, self.coach_message)

        my_break.refresh_from_db()
        other_break.refresh_from_db()
        self.assertIsNotNone(my_break.ended_at)
        self.assertIsNone(other_break.ended_at)

    def test_end_break_does_not_touch_already_closed_breaks(self):
        """An older, already-closed break must not have its ended_at rewritten."""
        old_break = self._open_break()
        original_ended_at = timezone.now() - timezone.timedelta(hours=2)
        old_break.ended_at = original_ended_at
        old_break.save(update_fields=["ended_at"])

        end_break(self.coach_state, self.params, self.coach_message)

        old_break.refresh_from_db()
        self.assertEqual(old_break.ended_at, original_ended_at)
        self.assertFalse(
            Action.objects.filter(
                user=self.user, action_type=ActionType.END_BREAK.value
            ).exists()
        )

    def test_end_break_returns_no_component_config_in_this_pr(self):
        """Locks the PR 8 / PR 14 split — basic close returns None; the
        intro-emission side effect ships in PR 14."""
        self._open_break()

        result = end_break(self.coach_state, self.params, self.coach_message)

        self.assertIsNone(result)
