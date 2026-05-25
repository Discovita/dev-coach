"""
Tests for services.action_handler.actions.transition_phase.

Integration tests covering coaching phase transitions, identity side
effects, Action audit logging, and the PR 13 Coaching-Phase-Videos
enrichment (flag-gated outro/intro auto-emit).
"""

from unittest.mock import patch

from django.test import TestCase, override_settings

from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from conftest import create_test_chat_message, create_test_user
from enums.action_type import ActionType
from enums.coaching_phase import CoachingPhase, SESSIONS
from enums.component_type import ComponentType
from enums.identity_state import IdentityState
from enums.message_role import MessageRole
from models.CoachChatResponse import CoachChatResponse
from models.components.ComponentConfig import ComponentConfig
from services.action_handler.actions.transition_phase import transition_phase
from services.action_handler.handler import apply_coach_actions
from services.action_handler.models import TransitionPhaseParams
from services.action_handler.models.actions import TransitionPhaseAction


class TransitionPhaseActionTests(TestCase):
    """Tests for the transition_phase action handler."""

    def setUp(self):
        self.user = create_test_user()
        self.coach_state = self.user.coach_state
        self.coach_state.current_phase = CoachingPhase.INTRODUCTION
        self.coach_state.save()
        self.coach_message = create_test_chat_message(
            self.user, role=MessageRole.COACH, content="Moving to next phase."
        )

    def test_updates_current_phase(self):
        """Should update coach_state.current_phase to the target phase."""
        params = TransitionPhaseParams(to_phase=CoachingPhase.GET_TO_KNOW_YOU)

        transition_phase(self.coach_state, params, self.coach_message)

        self.coach_state.refresh_from_db()
        self.assertEqual(
            self.coach_state.current_phase, CoachingPhase.GET_TO_KNOW_YOU
        )

    def test_logs_action_with_phase_labels(self):
        """Should create an Action record with readable phase labels in summary."""
        params = TransitionPhaseParams(to_phase=CoachingPhase.GET_TO_KNOW_YOU)

        transition_phase(self.coach_state, params, self.coach_message)

        action = Action.objects.filter(
            user=self.user, action_type=ActionType.TRANSITION_PHASE.value
        ).first()
        self.assertIsNotNone(action)
        self.assertIn("Introduction", action.result_summary)
        self.assertIn("Get to Know You", action.result_summary)

    @patch(
        "services.action_handler.actions.transition_phase.update_all_user_identities_to_accepted_state"
    )
    @patch(
        "services.action_handler.actions.transition_phase.set_current_identity_to_next_pending"
    )
    def test_entering_refinement_accepts_identities(
        self, mock_set_next, mock_accept_all
    ):
        """Transitioning to IDENTITY_REFINEMENT should accept all identities and set next pending."""
        params = TransitionPhaseParams(
            to_phase=CoachingPhase.IDENTITY_REFINEMENT
        )

        transition_phase(self.coach_state, params, self.coach_message)

        mock_accept_all.assert_called_once_with(self.coach_state)
        mock_set_next.assert_called_once_with(
            self.coach_state, IdentityState.REFINEMENT_COMPLETE
        )

    @patch(
        "services.action_handler.actions.transition_phase.set_current_identity_to_next_pending"
    )
    def test_entering_commitment_sets_next_pending(self, mock_set_next):
        """Transitioning to IDENTITY_COMMITMENT should set next pending identity."""
        params = TransitionPhaseParams(
            to_phase=CoachingPhase.IDENTITY_COMMITMENT
        )

        transition_phase(self.coach_state, params, self.coach_message)

        mock_set_next.assert_called_once_with(
            self.coach_state, IdentityState.COMMITMENT_COMPLETE
        )

    @patch(
        "services.action_handler.actions.transition_phase.set_current_identity_to_next_pending"
    )
    def test_entering_i_am_statement_sets_next_pending(self, mock_set_next):
        """Transitioning to I_AM_STATEMENT should set next pending identity."""
        params = TransitionPhaseParams(
            to_phase=CoachingPhase.I_AM_STATEMENT
        )

        transition_phase(self.coach_state, params, self.coach_message)

        mock_set_next.assert_called_once_with(
            self.coach_state, IdentityState.I_AM_COMPLETE
        )

    @patch(
        "services.action_handler.actions.transition_phase.update_all_user_identities_to_accepted_state"
    )
    @patch(
        "services.action_handler.actions.transition_phase.set_current_identity_to_next_pending"
    )
    def test_non_refinement_transition_skips_identity_updates(
        self, mock_set_next, mock_accept_all
    ):
        """Transitioning to a non-refinement phase should not call identity utilities."""
        params = TransitionPhaseParams(to_phase=CoachingPhase.GET_TO_KNOW_YOU)

        transition_phase(self.coach_state, params, self.coach_message)

        mock_accept_all.assert_not_called()
        mock_set_next.assert_not_called()


# ---------------------------------------------------------------------------
# PR 13 — Coaching Phase Videos enrichment (flag-gated)
# ---------------------------------------------------------------------------
#
# All boundary cases in the SESSIONS map. Each entry: (description,
# old_phase, new_phase, expected_outcome). `expected_outcome` is one of:
# - ("outro", session_key)  — emit outro for `session_key`
# - ("intro", session_key)  — emit intro for `session_key`
# - ("none", None)          — no video


_OUTRO_BOUNDARIES = [
    # (leaving_session, last_phase_of_session, first_phase_of_next_session)
    (
        "get_to_know_session",
        CoachingPhase.IDENTITY_WARMUP,
        CoachingPhase.IDENTITY_BRAINSTORMING,
    ),
    (
        "brainstorming_session",
        CoachingPhase.BRAINSTORMING_REVIEW,
        CoachingPhase.IDENTITY_REFINEMENT,
    ),
    (
        "refinement_session",
        CoachingPhase.ANYTHING_MISSING,
        CoachingPhase.IDENTITY_COMMITMENT,
    ),
    (
        "commitment_session",
        CoachingPhase.IDENTITY_COMMITMENT,
        CoachingPhase.I_AM_STATEMENT,
    ),
    (
        "i_am_session",
        CoachingPhase.I_AM_STATEMENT,
        CoachingPhase.IDENTITY_VISUALIZATION,
    ),
]


class TransitionPhaseSessionVideoEnrichmentTests(TestCase):
    """PR 13: flag-gated outro/intro auto-emit on session boundaries."""

    def setUp(self):
        self.user = create_test_user()
        self.coach_state = self.user.coach_state
        self.coach_message = create_test_chat_message(
            self.user, role=MessageRole.COACH, content="Let's move on."
        )

    def _set_phase(self, phase):
        self.coach_state.current_phase = phase
        self.coach_state.save()

    # --- Outro emission --------------------------------------------------

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=True)
    def test_attaches_outro_when_leaving_session_has_outro(self):
        """Every session-with-outro emits its outro on the boundary out."""
        for leaving_session, old_phase, new_phase in _OUTRO_BOUNDARIES:
            with self.subTest(session=leaving_session):
                ChatMessage.objects.all().delete()
                Action.objects.all().delete()
                self.coach_state.shown_videos = []
                self._set_phase(old_phase)
                coach_message = create_test_chat_message(
                    self.user, role=MessageRole.COACH, content="Transitioning."
                )

                params = TransitionPhaseParams(to_phase=new_phase)
                result = transition_phase(self.coach_state, params, coach_message)

                expected_key = SESSIONS[leaving_session]["outro"]
                self.assertIsInstance(result, ComponentConfig)
                self.assertEqual(
                    result.component_type, ComponentType.SESSION_VIDEO.value
                )
                self.assertEqual(result.video_key, expected_key)

                coach_message.refresh_from_db()
                self.assertIsNotNone(coach_message.component_config)
                self.assertEqual(
                    coach_message.component_config["component_type"],
                    ComponentType.SESSION_VIDEO.value,
                )
                self.assertEqual(
                    coach_message.component_config["video_key"], expected_key
                )

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=True)
    def test_outro_button_carries_ack_and_start_break_with_leaving_session_key(
        self,
    ):
        """Outro's Continue button is [ACK(outro_key), START_BREAK(leaving_session_key)]."""
        self._set_phase(CoachingPhase.IDENTITY_WARMUP)
        params = TransitionPhaseParams(to_phase=CoachingPhase.IDENTITY_BRAINSTORMING)

        result = transition_phase(self.coach_state, params, self.coach_message)

        self.assertIsNotNone(result)
        self.assertEqual(len(result.buttons), 1)
        actions = result.buttons[0].actions
        self.assertEqual(len(actions), 2)

        self.assertEqual(
            actions[0].action, ActionType.ACKNOWLEDGE_SESSION_VIDEO.value
        )
        self.assertEqual(
            actions[0].params, {"video_key": "get_to_know_session_outro"}
        )

        self.assertEqual(actions[1].action, ActionType.START_BREAK.value)
        self.assertEqual(
            actions[1].params, {"session_key": "get_to_know_session"}
        )

    # --- Intro emission --------------------------------------------------

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=True)
    def test_attaches_intro_when_leaving_session_has_no_outro_and_entering_has_intro(
        self,
    ):
        """INTRODUCTION → GET_TO_KNOW_YOU: welcome has no outro; emit get_to_know intro."""
        self._set_phase(CoachingPhase.INTRODUCTION)
        params = TransitionPhaseParams(to_phase=CoachingPhase.GET_TO_KNOW_YOU)

        result = transition_phase(self.coach_state, params, self.coach_message)

        self.assertIsInstance(result, ComponentConfig)
        self.assertEqual(result.component_type, ComponentType.SESSION_VIDEO.value)
        self.assertEqual(result.video_key, "get_to_know_session_intro")

        self.coach_message.refresh_from_db()
        self.assertEqual(
            self.coach_message.component_config["video_key"],
            "get_to_know_session_intro",
        )

    @override_settings(
        COACHING_PHASE_VIDEOS_ENABLED=True,
        AWS_STORAGE_BUCKET_NAME="test-bucket-foo",
    )
    def test_attached_component_embeds_video_name_and_video_url(self):
        """PR 20: the attached SESSION_VIDEO carries video_name + video_url
        from the registry so the FE renders without its own registry lookup."""
        self._set_phase(CoachingPhase.IDENTITY_WARMUP)
        params = TransitionPhaseParams(to_phase=CoachingPhase.IDENTITY_BRAINSTORMING)

        result = transition_phase(self.coach_state, params, self.coach_message)

        self.assertIsNotNone(result)
        self.assertEqual(result.video_name, "Get to Know You Outro")
        self.assertEqual(
            result.video_url,
            "https://test-bucket-foo.s3.amazonaws.com/"
            "media/session-videos/03-get-to-know-session-outro.mov",
        )
        # Persisted too, so a chat reload renders the same URL.
        self.coach_message.refresh_from_db()
        self.assertEqual(
            self.coach_message.component_config["video_name"],
            "Get to Know You Outro",
        )
        self.assertEqual(
            self.coach_message.component_config["video_url"],
            "https://test-bucket-foo.s3.amazonaws.com/"
            "media/session-videos/03-get-to-know-session-outro.mov",
        )

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=True)
    def test_intro_button_carries_only_ack_with_intro_key(self):
        """Intro's Continue button is [ACK(intro_key)] — no START_BREAK."""
        self._set_phase(CoachingPhase.INTRODUCTION)
        params = TransitionPhaseParams(to_phase=CoachingPhase.GET_TO_KNOW_YOU)

        result = transition_phase(self.coach_state, params, self.coach_message)

        self.assertIsNotNone(result)
        actions = result.buttons[0].actions
        self.assertEqual(len(actions), 1)
        self.assertEqual(
            actions[0].action, ActionType.ACKNOWLEDGE_SESSION_VIDEO.value
        )
        self.assertEqual(
            actions[0].params, {"video_key": "get_to_know_session_intro"}
        )

    # --- No-emit cases ---------------------------------------------------

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=True)
    def test_no_video_for_intra_session_transition(self):
        """GET_TO_KNOW_YOU → IDENTITY_WARMUP stays inside get_to_know_session."""
        self._set_phase(CoachingPhase.GET_TO_KNOW_YOU)
        params = TransitionPhaseParams(to_phase=CoachingPhase.IDENTITY_WARMUP)

        result = transition_phase(self.coach_state, params, self.coach_message)

        self.assertIsNone(result)
        self.coach_message.refresh_from_db()
        self.assertIsNone(self.coach_message.component_config)

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=True)
    def test_no_intro_when_entering_session_intro_already_in_shown_videos(self):
        """If the entering session's intro is already acked, don't re-emit."""
        self.coach_state.shown_videos = ["get_to_know_session_intro"]
        self._set_phase(CoachingPhase.INTRODUCTION)
        self.coach_state.save()

        params = TransitionPhaseParams(to_phase=CoachingPhase.GET_TO_KNOW_YOU)
        result = transition_phase(self.coach_state, params, self.coach_message)

        self.assertIsNone(result)
        self.coach_message.refresh_from_db()
        self.assertIsNone(self.coach_message.component_config)

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=True)
    def test_prefers_outro_over_intro_when_both_would_apply(self):
        """ANYTHING_MISSING → IDENTITY_COMMITMENT: outro (refinement) wins over intro (commitment)."""
        self._set_phase(CoachingPhase.ANYTHING_MISSING)
        params = TransitionPhaseParams(to_phase=CoachingPhase.IDENTITY_COMMITMENT)

        result = transition_phase(self.coach_state, params, self.coach_message)

        self.assertIsInstance(result, ComponentConfig)
        self.assertEqual(result.video_key, "refinement_session_outro")
        self.assertEqual(len(result.buttons[0].actions), 2)
        self.assertEqual(
            result.buttons[0].actions[1].params,
            {"session_key": "refinement_session"},
        )

    # --- Flag regression -------------------------------------------------

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=False)
    def test_no_video_when_flag_off(self):
        """With the flag off, the would-emit transition produces no component."""
        self._set_phase(CoachingPhase.INTRODUCTION)
        params = TransitionPhaseParams(to_phase=CoachingPhase.GET_TO_KNOW_YOU)

        result = transition_phase(self.coach_state, params, self.coach_message)

        self.assertIsNone(result)
        self.coach_message.refresh_from_db()
        self.assertIsNone(self.coach_message.component_config)

    def test_phase_change_unchanged_in_both_flag_branches(self):
        """current_phase advances identically whether the flag is on or off."""
        for flag in (False, True):
            with self.subTest(flag=flag):
                ChatMessage.objects.all().delete()
                Action.objects.all().delete()
                self._set_phase(CoachingPhase.INTRODUCTION)
                coach_message = create_test_chat_message(
                    self.user, role=MessageRole.COACH, content="Transitioning."
                )

                params = TransitionPhaseParams(
                    to_phase=CoachingPhase.GET_TO_KNOW_YOU
                )
                with override_settings(COACHING_PHASE_VIDEOS_ENABLED=flag):
                    transition_phase(self.coach_state, params, coach_message)

                self.coach_state.refresh_from_db()
                self.assertEqual(
                    self.coach_state.current_phase,
                    CoachingPhase.GET_TO_KNOW_YOU,
                )

    # --- Integration through apply_coach_actions -------------------------

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=True)
    def test_apply_coach_actions_propagates_session_video_component(self):
        """End-to-end: an LLM turn emitting transition_phase yields the video card on the coach response.

        Verifies the orchestrator path that PR 13 hands off to: dispatching
        a `CoachChatResponse` with a `transition_phase` action through
        `apply_coach_actions` returns a `(CoachState, ComponentConfig)`
        tuple where the component is the SESSION_VIDEO card, AND the
        coach_message row carries the same component_config in DB so the
        history serializer (PR 11) renders it on subsequent turns.
        """
        self._set_phase(CoachingPhase.INTRODUCTION)
        coach_response = CoachChatResponse(
            message="Let's move on to getting to know you.",
            transition_phase=TransitionPhaseAction(
                params=TransitionPhaseParams(
                    to_phase=CoachingPhase.GET_TO_KNOW_YOU
                )
            ),
        )

        updated_state, component_config = apply_coach_actions(
            self.coach_state, coach_response, self.coach_message
        )

        self.assertEqual(
            updated_state.current_phase, CoachingPhase.GET_TO_KNOW_YOU
        )
        self.assertIsInstance(component_config, ComponentConfig)
        self.assertEqual(
            component_config.component_type, ComponentType.SESSION_VIDEO.value
        )
        self.assertEqual(
            component_config.video_key, "get_to_know_session_intro"
        )

        self.coach_message.refresh_from_db()
        self.assertEqual(
            self.coach_message.component_config["video_key"],
            "get_to_know_session_intro",
        )
        self.assertEqual(
            self.coach_message.component_config["component_type"],
            ComponentType.SESSION_VIDEO.value,
        )
