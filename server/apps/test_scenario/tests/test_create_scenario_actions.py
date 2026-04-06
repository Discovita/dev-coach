"""
Tests for apps.test_scenario.utils.create_scenario_actions.

Verifies that Action objects are correctly created from template data
with proper coach message linking.
"""

from unittest.mock import patch

from django.test import TestCase

from apps.actions.models import Action
from apps.test_scenario.models import TestScenario
from apps.test_scenario.utils.create_scenario_actions import create_scenario_actions
from conftest import create_test_user, create_test_chat_message
from enums.action_type import ActionType
from enums.message_role import MessageRole


class CreateScenarioActionsTests(TestCase):
    """Tests for create_scenario_actions utility."""

    def setUp(self):
        self.user = create_test_user()
        self.scenario = TestScenario.objects.create(
            name="Test Scenario",
            template={},
        )
        self.coach_msg = create_test_chat_message(
            self.user, role=MessageRole.COACH, content="Coach says hello"
        )

    @patch(
        "apps.test_scenario.utils.create_scenario_actions.resolve_scenario_coach_message"
    )
    def test_creates_action_from_template(self, mock_resolve):
        """Should create an Action for each entry in template actions."""
        mock_resolve.return_value = self.coach_msg
        template = {
            "actions": [
                {
                    "action_type": ActionType.CREATE_IDENTITY.value,
                    "parameters": {"name": "Visionary"},
                    "result_summary": "Created Visionary",
                }
            ]
        }

        create_scenario_actions(
            self.scenario, template, self.user, {}
        )

        actions = Action.objects.filter(user=self.user)
        self.assertEqual(actions.count(), 1)
        self.assertEqual(
            actions.first().action_type, ActionType.CREATE_IDENTITY.value
        )

    @patch(
        "apps.test_scenario.utils.create_scenario_actions.resolve_scenario_coach_message"
    )
    def test_creates_multiple_actions(self, mock_resolve):
        """Should create multiple Action objects from template."""
        mock_resolve.return_value = self.coach_msg
        template = {
            "actions": [
                {
                    "action_type": ActionType.CREATE_IDENTITY.value,
                    "parameters": {},
                },
                {
                    "action_type": ActionType.TRANSITION_PHASE.value,
                    "parameters": {"to_phase": "get_to_know_you"},
                },
            ]
        }

        create_scenario_actions(
            self.scenario, template, self.user, {}
        )

        self.assertEqual(Action.objects.filter(user=self.user).count(), 2)

    @patch(
        "apps.test_scenario.utils.create_scenario_actions.resolve_scenario_coach_message"
    )
    def test_deletes_existing_scenario_actions_first(self, mock_resolve):
        """Should delete existing actions for this user+scenario before creating new ones."""
        mock_resolve.return_value = self.coach_msg
        Action.objects.create(
            user=self.user,
            test_scenario=self.scenario,
            action_type=ActionType.CREATE_IDENTITY.value,
            parameters={},
            coach_message=self.coach_msg,
        )

        template = {
            "actions": [
                {
                    "action_type": ActionType.TRANSITION_PHASE.value,
                    "parameters": {},
                }
            ]
        }

        create_scenario_actions(
            self.scenario, template, self.user, {}
        )

        actions = Action.objects.filter(user=self.user)
        self.assertEqual(actions.count(), 1)
        self.assertEqual(
            actions.first().action_type, ActionType.TRANSITION_PHASE.value
        )

    @patch(
        "apps.test_scenario.utils.create_scenario_actions.resolve_scenario_coach_message"
    )
    def test_links_coach_message_via_resolver(self, mock_resolve):
        """Should link each action to its coach message via resolve_scenario_coach_message."""
        mock_resolve.return_value = self.coach_msg
        template = {
            "actions": [
                {
                    "action_type": ActionType.CREATE_IDENTITY.value,
                    "parameters": {},
                }
            ]
        }

        create_scenario_actions(
            self.scenario, template, self.user, {}
        )

        action = Action.objects.first()
        self.assertEqual(action.coach_message, self.coach_msg)
        mock_resolve.assert_called_once()

    @patch(
        "apps.test_scenario.utils.create_scenario_actions.resolve_scenario_coach_message"
    )
    def test_empty_actions_list(self, mock_resolve):
        """Should handle empty actions list without error."""
        template = {"actions": []}
        create_scenario_actions(
            self.scenario, template, self.user, {}
        )
        self.assertEqual(Action.objects.filter(user=self.user).count(), 0)
