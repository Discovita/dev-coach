"""
Tests for services.action_handler.actions.end_break.

PR 8 ships the **basic close**: stamp `ended_at` on the user's single open
Break and write an Action audit row. PR 14 extends the handler with
flag-gated **intro emission**: after closing the break, if `current_phase`
is the first phase of a session whose intro hasn't been acknowledged yet,
return a SESSION_VIDEO `ComponentConfig` for that intro so the
orchestrator's skip-LLM-on-component rule fires.

PR 7's START_BREAK enforces at-most-one-open-break-per-user, so the
lookup here can safely use `.filter().first()` and treat the no-open-break
case as a no-op (defensive against duplicate clicks).
"""

from django.test import TestCase, override_settings
from django.utils import timezone

from apps.actions.models import Action
from apps.coach.utils.apply_user_component_actions import (
    apply_user_component_actions,
)
from apps.coach_states.models import Break
from conftest import create_test_chat_message, create_test_user
from enums.action_type import ActionType
from enums.coaching_phase import CoachingPhase, SESSIONS
from enums.component_type import ComponentType
from enums.message_role import MessageRole
from models.components.ComponentConfig import ComponentConfig
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


# ---------------------------------------------------------------------------
# PR 14 — END_BREAK intro auto-emit enrichment (flag-gated)
# ---------------------------------------------------------------------------
#
# After stamping `ended_at`, if `coach_state.current_phase` is the first
# phase of a session whose intro hasn't been acknowledged yet, the handler
# returns a SESSION_VIDEO `ComponentConfig` so the orchestrator's
# skip-LLM-on-component rule fires.
#
# Realistic post-break boundaries — for each, the user was on a break
# triggered by the prior session's outro and `current_phase` has already
# advanced into the new session's first phase by the time END_BREAK runs.
_POST_BREAK_INTRO_BOUNDARIES = [
    # (triggered_by_session, current_phase, expected_intro_key)
    (
        "get_to_know_session",
        CoachingPhase.IDENTITY_BRAINSTORMING,
        "brainstorming_session_intro",
    ),
    (
        "brainstorming_session",
        CoachingPhase.IDENTITY_REFINEMENT,
        "refinement_session_intro",
    ),
    (
        "refinement_session",
        CoachingPhase.IDENTITY_COMMITMENT,
        "commitment_session_intro",
    ),
    (
        "commitment_session",
        CoachingPhase.I_AM_STATEMENT,
        "i_am_session_intro",
    ),
    (
        "i_am_session",
        CoachingPhase.IDENTITY_VISUALIZATION,
        "visualization_session_intro",
    ),
]


class EndBreakSessionVideoEnrichmentTests(TestCase):
    """PR 14: flag-gated post-break intro auto-emit."""

    def setUp(self):
        self.user = create_test_user()
        self.coach_state = self.user.coach_state
        # In production, the `coach_message` passed to END_BREAK is the
        # user's "I'm ready" message (END_BREAK is dispatched via the
        # canned-response button, see Decision 7). Reuse that here so the
        # Action audit row links to a real ChatMessage.
        self.user_message = create_test_chat_message(
            self.user,
            role=MessageRole.USER,
            content="I'm ready",
        )
        self.params = EndBreakParams()

    def _open_break(self, triggered_by_session="get_to_know_session"):
        return Break.objects.create(
            user=self.user, triggered_by_session=triggered_by_session
        )

    def _set_phase_and_shown_videos(self, phase, shown_videos=None):
        self.coach_state.current_phase = phase
        self.coach_state.shown_videos = shown_videos or []
        self.coach_state.save()

    # --- Intro emission --------------------------------------------------

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=True)
    def test_returns_intro_component_when_current_phase_is_session_first_phase_with_unacked_intro(
        self,
    ):
        """Every post-break boundary emits the new session's intro card."""
        for (
            triggered_by_session,
            current_phase,
            expected_intro_key,
        ) in _POST_BREAK_INTRO_BOUNDARIES:
            with self.subTest(session=triggered_by_session):
                Break.objects.filter(user=self.user).delete()
                Action.objects.filter(user=self.user).delete()
                self._set_phase_and_shown_videos(current_phase, shown_videos=[])
                open_break = self._open_break(
                    triggered_by_session=triggered_by_session
                )

                result = end_break(
                    self.coach_state, self.params, self.user_message
                )

                self.assertIsInstance(result, ComponentConfig)
                self.assertEqual(
                    result.component_type, ComponentType.SESSION_VIDEO.value
                )
                self.assertEqual(result.video_key, expected_intro_key)

                # Still closes the break.
                open_break.refresh_from_db()
                self.assertIsNotNone(open_break.ended_at)

                # Handler must NOT write component_config to the passed
                # coach_message — that param is the USER's "I'm ready"
                # message in this path. The orchestrator owns the coach-
                # message creation + persistence in the skip-LLM branch.
                self.user_message.refresh_from_db()
                self.assertIsNone(self.user_message.component_config)

    @override_settings(
        COACHING_PHASE_VIDEOS_ENABLED=True,
        AWS_STORAGE_BUCKET_NAME="test-bucket-foo",
    )
    def test_returned_component_embeds_video_name_and_video_url(self):
        """PR 20: the returned intro carries video_name + video_url so the
        FE renders without its own registry lookup."""
        self._set_phase_and_shown_videos(CoachingPhase.IDENTITY_BRAINSTORMING)
        self._open_break(triggered_by_session="get_to_know_session")

        result = end_break(self.coach_state, self.params, self.user_message)

        self.assertIsNotNone(result)
        self.assertEqual(result.video_name, "Brainstorming Intro")
        self.assertEqual(
            result.video_url,
            "https://test-bucket-foo.s3.amazonaws.com/"
            "session-videos/04-brainstorming-session-intro.mov",
        )

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=True)
    def test_intro_button_carries_only_ack_with_intro_key(self):
        """Intro's Continue button is [ACK(intro_key)] — no START_BREAK."""
        self._set_phase_and_shown_videos(CoachingPhase.IDENTITY_BRAINSTORMING)
        self._open_break(triggered_by_session="get_to_know_session")

        result = end_break(self.coach_state, self.params, self.user_message)

        self.assertIsNotNone(result)
        self.assertEqual(len(result.buttons), 1)
        actions = result.buttons[0].actions
        self.assertEqual(len(actions), 1)
        self.assertEqual(
            actions[0].action, ActionType.ACKNOWLEDGE_SESSION_VIDEO.value
        )
        self.assertEqual(
            actions[0].params, {"video_key": "brainstorming_session_intro"}
        )

    # --- No-emit cases ---------------------------------------------------

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=True)
    def test_no_intro_when_intro_already_acked(self):
        """Idempotency: if the intro is already in shown_videos, don't re-emit."""
        self._set_phase_and_shown_videos(
            CoachingPhase.IDENTITY_BRAINSTORMING,
            shown_videos=["brainstorming_session_intro"],
        )
        open_break = self._open_break(triggered_by_session="get_to_know_session")

        result = end_break(self.coach_state, self.params, self.user_message)

        self.assertIsNone(result)
        open_break.refresh_from_db()
        self.assertIsNotNone(open_break.ended_at)

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=True)
    def test_no_intro_when_current_phase_is_not_first_phase_of_session(self):
        """Edge case: break closing mid-session should not emit an intro.

        E.g. `IDENTITY_WARMUP` is the second phase of `get_to_know_session`;
        a break closing on it must not re-emit that session's intro card.
        """
        self._set_phase_and_shown_videos(CoachingPhase.IDENTITY_WARMUP)
        open_break = self._open_break(triggered_by_session="get_to_know_session")

        result = end_break(self.coach_state, self.params, self.user_message)

        self.assertIsNone(result)
        open_break.refresh_from_db()
        self.assertIsNotNone(open_break.ended_at)

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=False)
    def test_no_intro_when_flag_off(self):
        """With the flag off, the would-emit close produces no component."""
        self._set_phase_and_shown_videos(CoachingPhase.IDENTITY_BRAINSTORMING)
        open_break = self._open_break(triggered_by_session="get_to_know_session")

        result = end_break(self.coach_state, self.params, self.user_message)

        self.assertIsNone(result)
        open_break.refresh_from_db()
        self.assertIsNotNone(open_break.ended_at)

    # --- Core behavior preserved ----------------------------------------

    def test_still_closes_break_in_both_flag_branches(self):
        """ended_at is stamped whether the flag is on or off."""
        for flag in (False, True):
            with self.subTest(flag=flag):
                Break.objects.filter(user=self.user).delete()
                Action.objects.filter(user=self.user).delete()
                self._set_phase_and_shown_videos(
                    CoachingPhase.IDENTITY_BRAINSTORMING
                )
                open_break = self._open_break(
                    triggered_by_session="get_to_know_session"
                )

                with override_settings(COACHING_PHASE_VIDEOS_ENABLED=flag):
                    end_break(self.coach_state, self.params, self.user_message)

                open_break.refresh_from_db()
                self.assertIsNotNone(open_break.ended_at)

                action = Action.objects.filter(
                    user=self.user, action_type=ActionType.END_BREAK.value
                ).first()
                self.assertIsNotNone(action)

    # --- Integration through apply_user_component_actions ----------------

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=True)
    def test_returned_component_triggers_skip_llm_rule_via_apply_user_component_actions(
        self,
    ):
        """End-to-end: user clicks I'm Ready → END_BREAK closes the break and
        the returned SESSION_VIDEO intro propagates out of
        `apply_user_component_actions`, so the orchestrator can apply the
        skip-LLM-on-component rule (PR 10) on the next turn.
        """
        self._set_phase_and_shown_videos(CoachingPhase.IDENTITY_BRAINSTORMING)
        open_break = self._open_break(triggered_by_session="get_to_know_session")

        component_config = apply_user_component_actions(
            self.coach_state,
            self.user_message,
            [{"action": ActionType.END_BREAK.value, "params": {}}],
        )

        self.assertIsInstance(component_config, ComponentConfig)
        self.assertEqual(
            component_config.component_type, ComponentType.SESSION_VIDEO.value
        )
        self.assertEqual(
            component_config.video_key, "brainstorming_session_intro"
        )

        open_break.refresh_from_db()
        self.assertIsNotNone(open_break.ended_at)

        # And the audit row was written.
        self.assertTrue(
            Action.objects.filter(
                user=self.user, action_type=ActionType.END_BREAK.value
            ).exists()
        )

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=True)
    def test_intro_keys_match_sessions_map(self):
        """Self-check that the parametrized expected keys agree with SESSIONS."""
        for (
            triggered_by_session,
            current_phase,
            expected_intro_key,
        ) in _POST_BREAK_INTRO_BOUNDARIES:
            with self.subTest(session=triggered_by_session):
                entering_session = next(
                    key
                    for key, cfg in SESSIONS.items()
                    if current_phase in cfg["phases"]
                )
                self.assertEqual(
                    SESSIONS[entering_session]["intro"], expected_intro_key
                )
