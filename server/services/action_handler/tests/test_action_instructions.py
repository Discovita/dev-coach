"""
Tests for services.action_handler.utils.action_instructions.

Verifies that action instruction generation produces valid markdown
instruction blocks for the prompt system.
"""

from django.test import SimpleTestCase

from enums.action_type import ActionType
from services.action_handler.utils.action_instructions import (
    ACTION_INSTRUCTIONS,
    ACTION_PARAMS,
    get_action_instructions,
)


class ActionParamsRegistryTests(SimpleTestCase):
    """Tests for the ACTION_PARAMS mapping."""

    def test_every_entry_has_description(self):
        """Each ACTION_PARAMS entry should have a 'description' key."""
        for action_type, info in ACTION_PARAMS.items():
            self.assertIn(
                "description",
                info,
                f"{action_type} missing 'description'",
            )

    def test_every_entry_has_model(self):
        """Each ACTION_PARAMS entry should have a 'model' key."""
        for action_type, info in ACTION_PARAMS.items():
            self.assertIn(
                "model",
                info,
                f"{action_type} missing 'model'",
            )

    def test_models_are_pydantic_base_models(self):
        """Each model should be a Pydantic BaseModel subclass."""
        from pydantic import BaseModel

        for action_type, info in ACTION_PARAMS.items():
            self.assertTrue(
                issubclass(info["model"], BaseModel),
                f"{action_type} model is not a BaseModel subclass",
            )


class ActionInstructionsTests(SimpleTestCase):
    """Tests for the ACTION_INSTRUCTIONS dict and get_action_instructions."""

    def test_instructions_generated_for_all_params(self):
        """Every entry in ACTION_PARAMS should have a corresponding instruction."""
        for action_type in ACTION_PARAMS:
            self.assertIn(
                action_type,
                ACTION_INSTRUCTIONS,
                f"{action_type} missing from ACTION_INSTRUCTIONS",
            )

    def test_instruction_contains_action_name(self):
        """Each instruction should reference the action type value."""
        for action_type, instruction in ACTION_INSTRUCTIONS.items():
            self.assertIn(
                action_type.value,
                instruction,
                f"Instruction for {action_type} doesn't contain its value",
            )

    def test_instruction_contains_json_schema_block(self):
        """Each instruction should include a JSON schema code block."""
        for action_type, instruction in ACTION_INSTRUCTIONS.items():
            self.assertIn(
                "```json",
                instruction,
                f"Instruction for {action_type} missing JSON block",
            )


class GetActionInstructionsTests(SimpleTestCase):
    """Tests for get_action_instructions function."""

    def test_empty_list_returns_empty_string(self):
        """No action types should produce empty instructions."""
        result = get_action_instructions([])
        self.assertEqual(result, "")

    def test_single_action_returns_formatted_output(self):
        """A single action should return header + instruction + footer."""
        result = get_action_instructions([ActionType.CREATE_IDENTITY])
        self.assertIn("# Available Actions", result)
        self.assertIn("create_identity", result)
        self.assertIn("params field must match the schema", result)

    def test_multiple_actions_includes_all(self):
        """Multiple actions should all appear in the output."""
        actions = [
            ActionType.CREATE_IDENTITY,
            ActionType.TRANSITION_PHASE,
            ActionType.ACCEPT_IDENTITY,
        ]
        result = get_action_instructions(actions)
        for action in actions:
            self.assertIn(action.value, result)

    def test_unknown_action_type_is_skipped_gracefully(self):
        """ActionType not in ACTION_INSTRUCTIONS shouldn't crash."""
        result = get_action_instructions([ActionType.CREATE_IDENTITY])
        self.assertIn("create_identity", result)
