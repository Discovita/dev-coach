"""
Tests for apps.test_scenario.utils.create_scenario_coach_state.

Verifies that template coach_state data is correctly applied to the
auto-created CoachState for a test scenario user.
"""

from django.test import TestCase

from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from apps.test_scenario.models import TestScenario
from apps.test_scenario.utils.create_scenario_coach_state import (
    create_scenario_coach_state,
)
from conftest import create_test_user
from enums.coaching_phase import CoachingPhase
from enums.identity_category import IdentityCategory


class CreateScenarioCoachStateTests(TestCase):
    """Tests for create_scenario_coach_state utility."""

    def setUp(self):
        self.user = create_test_user()
        self.scenario = TestScenario.objects.create(
            name="Test Scenario",
            template={},
        )

    def test_updates_current_phase(self):
        """Should set current_phase from template data."""
        template = {
            "coach_state": {
                "current_phase": CoachingPhase.IDENTITY_BRAINSTORMING,
            }
        }
        result = create_scenario_coach_state(
            self.scenario, template, self.user, {}
        )
        self.assertEqual(
            result.current_phase, CoachingPhase.IDENTITY_BRAINSTORMING
        )

    def test_sets_identity_focus(self):
        """Should set identity_focus from template data."""
        template = {
            "coach_state": {
                "current_phase": CoachingPhase.INTRODUCTION,
                "identity_focus": IdentityCategory.HEALTH,
            }
        }
        result = create_scenario_coach_state(
            self.scenario, template, self.user, {}
        )
        self.assertEqual(result.identity_focus, IdentityCategory.HEALTH)

    def test_resolves_current_identity_from_created_map(self):
        """Should set current_identity from created_identities map."""
        identity = Identity.objects.create(
            user=self.user,
            name="Visionary",
            category=IdentityCategory.PASSIONS,
        )
        template = {
            "coach_state": {
                "current_phase": CoachingPhase.IDENTITY_REFINEMENT,
                "current_identity": "Visionary",
            }
        }
        result = create_scenario_coach_state(
            self.scenario, template, self.user, {"Visionary": identity}
        )
        self.assertEqual(result.current_identity, identity)

    def test_missing_current_identity_logs_warning(self):
        """Should handle missing identity name gracefully."""
        template = {
            "coach_state": {
                "current_phase": CoachingPhase.IDENTITY_REFINEMENT,
                "current_identity": "NonExistent",
            }
        }
        result = create_scenario_coach_state(
            self.scenario, template, self.user, {}
        )
        self.assertIsNone(result.current_identity)

    def test_sets_test_scenario_on_coach_state(self):
        """Should set the test_scenario FK on the CoachState."""
        template = {
            "coach_state": {
                "current_phase": CoachingPhase.INTRODUCTION,
            }
        }
        result = create_scenario_coach_state(
            self.scenario, template, self.user, {}
        )
        self.assertEqual(result.test_scenario, self.scenario)

    def test_ignores_unknown_fields(self):
        """Should silently ignore fields not on the CoachState model."""
        template = {
            "coach_state": {
                "current_phase": CoachingPhase.INTRODUCTION,
                "not_a_real_field": "ignored",
            }
        }
        result = create_scenario_coach_state(
            self.scenario, template, self.user, {}
        )
        self.assertFalse(hasattr(result, "not_a_real_field"))

    def test_strips_proposed_identity_from_data(self):
        """Should pop proposed_identity from coach_state data without error."""
        template = {
            "coach_state": {
                "current_phase": CoachingPhase.INTRODUCTION,
                "proposed_identity": "SomeName",
            }
        }
        result = create_scenario_coach_state(
            self.scenario, template, self.user, {}
        )
        self.assertIsNotNone(result)

    def test_applies_shown_videos_from_template(self):
        """Coaching Phase Videos (PR 111): shown_videos in the template must
        land on the instantiated CoachState so re-played scenarios skip the
        already-acked intros/outros."""
        template = {
            "coach_state": {
                "current_phase": CoachingPhase.INTRODUCTION,
                "shown_videos": [
                    "welcome_session_intro",
                    "get_to_know_session_intro",
                ],
            }
        }
        result = create_scenario_coach_state(
            self.scenario, template, self.user, {}
        )
        self.assertEqual(
            result.shown_videos,
            ["welcome_session_intro", "get_to_know_session_intro"],
        )
