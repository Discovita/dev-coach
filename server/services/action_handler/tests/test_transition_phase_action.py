"""
Tests for services.action_handler.actions.transition_phase.

Integration tests that verify coaching phase transitions, side effects
(identity state updates), and Action audit logging.
"""

from unittest.mock import patch

from django.test import TestCase

from apps.actions.models import Action
from apps.identities.models import Identity
from apps.users.models import User
from conftest import create_test_user, create_test_chat_message, create_test_identity
from enums.action_type import ActionType
from enums.coaching_phase import CoachingPhase
from enums.identity_category import IdentityCategory
from enums.identity_state import IdentityState
from enums.message_role import MessageRole
from services.action_handler.actions.transition_phase import transition_phase
from services.action_handler.models import TransitionPhaseParams


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
