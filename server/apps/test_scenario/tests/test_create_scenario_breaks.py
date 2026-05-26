"""
Tests for create_scenario_breaks function (Coaching Phase Videos PR 111).
"""

from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from apps.coach_states.models import Break
from apps.test_scenario.models import TestScenario
from apps.test_scenario.utils.create_scenario_breaks import create_scenario_breaks
from conftest import create_test_chat_message, create_test_user
from enums.message_role import MessageRole


class CreateScenarioBreaksTests(TestCase):
    """Tests for create_scenario_breaks utility."""

    def setUp(self):
        self.user = create_test_user()
        self.scenario = TestScenario.objects.create(
            name="Test Scenario",
            template={},
        )
        self.coach_msg = create_test_chat_message(
            self.user, role=MessageRole.COACH, content="Take a break"
        )

    @patch(
        "apps.test_scenario.utils.create_scenario_breaks.resolve_scenario_coach_message"
    )
    def test_creates_break_from_template(self, mock_resolve):
        """Should create a Break row for each entry in template breaks."""
        mock_resolve.return_value = self.coach_msg
        template = {
            "breaks": [
                {"triggered_by_session": "get_to_know_session"},
            ]
        }

        create_scenario_breaks(self.scenario, template, self.user, {})

        breaks = Break.objects.filter(user=self.user)
        self.assertEqual(breaks.count(), 1)
        self.assertEqual(breaks.first().triggered_by_session, "get_to_know_session")

    @patch(
        "apps.test_scenario.utils.create_scenario_breaks.resolve_scenario_coach_message"
    )
    def test_creates_multiple_breaks(self, mock_resolve):
        """Should create multiple Break rows from template."""
        mock_resolve.return_value = self.coach_msg
        template = {
            "breaks": [
                {"triggered_by_session": "get_to_know_session"},
                {"triggered_by_session": "brainstorming_session"},
            ]
        }

        create_scenario_breaks(self.scenario, template, self.user, {})

        self.assertEqual(Break.objects.filter(user=self.user).count(), 2)

    @patch(
        "apps.test_scenario.utils.create_scenario_breaks.resolve_scenario_coach_message"
    )
    def test_deletes_existing_breaks_first(self, mock_resolve):
        """Should delete the user's existing Break rows before creating new ones."""
        mock_resolve.return_value = self.coach_msg
        Break.objects.create(
            user=self.user,
            triggered_by_session="old_session",
        )

        template = {
            "breaks": [
                {"triggered_by_session": "brainstorming_session"},
            ]
        }
        create_scenario_breaks(self.scenario, template, self.user, {})

        breaks = Break.objects.filter(user=self.user)
        self.assertEqual(breaks.count(), 1)
        self.assertEqual(breaks.first().triggered_by_session, "brainstorming_session")

    @patch(
        "apps.test_scenario.utils.create_scenario_breaks.resolve_scenario_coach_message"
    )
    def test_links_coach_message_via_resolver(self, mock_resolve):
        """Should link each break to its coach message via the resolver."""
        mock_resolve.return_value = self.coach_msg
        template = {
            "breaks": [
                {
                    "triggered_by_session": "get_to_know_session",
                    "original_coach_message_id": str(self.coach_msg.id),
                }
            ]
        }

        create_scenario_breaks(self.scenario, template, self.user, {})

        br = Break.objects.first()
        self.assertEqual(br.coach_message, self.coach_msg)
        mock_resolve.assert_called_once()

    @patch(
        "apps.test_scenario.utils.create_scenario_breaks.resolve_scenario_coach_message"
    )
    def test_preserves_ended_at(self, mock_resolve):
        """A closed break in the template should arrive closed."""
        mock_resolve.return_value = self.coach_msg
        ended = timezone.now() - timedelta(minutes=10)
        template = {
            "breaks": [
                {
                    "triggered_by_session": "i_am_session",
                    "ended_at": ended.isoformat(),
                }
            ]
        }

        create_scenario_breaks(self.scenario, template, self.user, {})

        br = Break.objects.first()
        self.assertIsNotNone(br.ended_at)

    @patch(
        "apps.test_scenario.utils.create_scenario_breaks.resolve_scenario_coach_message"
    )
    def test_preserves_started_at_via_update(self, mock_resolve):
        """`started_at` is auto_now_add on the model — the creator must
        use `.update()` to bypass that so the captured timestamp survives
        instantiation."""
        mock_resolve.return_value = self.coach_msg
        # Pick a clearly-past timestamp that the auto_now_add default
        # would never produce on its own.
        target = timezone.now() - timedelta(days=3)
        template = {
            "breaks": [
                {
                    "triggered_by_session": "commitment_session",
                    "started_at": target.isoformat(),
                }
            ]
        }

        create_scenario_breaks(self.scenario, template, self.user, {})

        br = Break.objects.first()
        self.assertAlmostEqual(
            br.started_at.timestamp(),
            target.timestamp(),
            delta=2,  # tolerate isoformat round-trip + DB precision
        )

    @patch(
        "apps.test_scenario.utils.create_scenario_breaks.resolve_scenario_coach_message"
    )
    def test_open_break_leaves_ended_at_null(self, mock_resolve):
        """Open breaks in the template (no ended_at) should remain open."""
        mock_resolve.return_value = self.coach_msg
        template = {
            "breaks": [
                {"triggered_by_session": "refinement_session"},
            ]
        }

        create_scenario_breaks(self.scenario, template, self.user, {})

        br = Break.objects.first()
        self.assertIsNone(br.ended_at)

    @patch(
        "apps.test_scenario.utils.create_scenario_breaks.resolve_scenario_coach_message"
    )
    def test_isolates_other_users_breaks(self, mock_resolve):
        """Should not delete breaks belonging to other users."""
        mock_resolve.return_value = self.coach_msg
        other = create_test_user(email="other@example.com")
        Break.objects.create(user=other, triggered_by_session="get_to_know_session")

        template = {
            "breaks": [
                {"triggered_by_session": "brainstorming_session"},
            ]
        }
        create_scenario_breaks(self.scenario, template, self.user, {})

        self.assertEqual(Break.objects.filter(user=other).count(), 1)
        self.assertEqual(Break.objects.filter(user=self.user).count(), 1)

    @patch(
        "apps.test_scenario.utils.create_scenario_breaks.resolve_scenario_coach_message"
    )
    def test_empty_breaks_list(self, mock_resolve):
        """Should handle empty breaks list without error."""
        template = {"breaks": []}
        create_scenario_breaks(self.scenario, template, self.user, {})
        self.assertEqual(Break.objects.filter(user=self.user).count(), 0)
