"""
Tests for services.action_handler.utils.dynamic_schema.build_dynamic_response_format.

Verifies that the dynamic Pydantic model builder correctly constructs
response models from lists of allowed action type strings.
"""

from django.test import SimpleTestCase
from pydantic import BaseModel, ValidationError

from enums.action_type import ActionType
from services.action_handler.utils.dynamic_schema import (
    ACTION_TYPE_TO_MODEL,
    build_dynamic_response_format,
)


class BuildDynamicResponseFormatTests(SimpleTestCase):
    """Tests for the build_dynamic_response_format function."""

    def test_empty_actions_returns_message_only_model(self):
        """With no allowed actions, only 'message' should be a field."""
        model_cls = build_dynamic_response_format([])
        fields = model_cls.model_fields
        self.assertIn("message", fields)
        self.assertEqual(len(fields), 1)

    def test_message_field_is_required(self):
        """The message field should be required (no default)."""
        model_cls = build_dynamic_response_format([])
        with self.assertRaises(ValidationError):
            model_cls()

    def test_single_action_produces_optional_field(self):
        """A single allowed action should add one optional field."""
        model_cls = build_dynamic_response_format(
            [ActionType.CREATE_IDENTITY.value]
        )
        fields = model_cls.model_fields
        self.assertIn("message", fields)
        self.assertIn("create_identity", fields)
        self.assertEqual(len(fields), 2)

    def test_action_field_accepts_none(self):
        """Action fields should accept None as a value (Optional type)."""
        model_cls = build_dynamic_response_format(
            [ActionType.CREATE_IDENTITY.value]
        )
        instance = model_cls(message="Hello", create_identity=None)
        self.assertIsNone(instance.create_identity)

    def test_multiple_actions(self):
        """Multiple allowed actions should each get their own field."""
        actions = [
            ActionType.CREATE_IDENTITY.value,
            ActionType.TRANSITION_PHASE.value,
            ActionType.ACCEPT_IDENTITY.value,
        ]
        model_cls = build_dynamic_response_format(actions)
        fields = model_cls.model_fields
        self.assertEqual(len(fields), 4)
        for action_value in actions:
            self.assertIn(action_value, fields)

    def test_action_type_to_model_registry_completeness(self):
        """Every ActionType that is in the handler registry should be in ACTION_TYPE_TO_MODEL."""
        from services.action_handler.handler import ACTION_REGISTRY

        for action_value in ACTION_REGISTRY:
            try:
                action_type = ActionType(action_value)
            except ValueError:
                continue
            self.assertIn(
                action_type,
                ACTION_TYPE_TO_MODEL,
                f"{action_type} is in ACTION_REGISTRY but not in ACTION_TYPE_TO_MODEL",
            )

    def test_model_rejects_extra_fields(self):
        """Generated model should reject extra fields (config extra=forbid)."""
        model_cls = build_dynamic_response_format([])
        with self.assertRaises(ValidationError):
            model_cls(message="Hello", unexpected_field="bad")

    def test_accepts_string_action_types(self):
        """Should accept plain string values, not just ActionType enums."""
        model_cls = build_dynamic_response_format(["create_identity"])
        fields = model_cls.model_fields
        self.assertIn("create_identity", fields)

    def test_all_llm_callable_actions_can_build(self):
        """Every LLM-callable ActionType should be buildable without error.

        User-button-only actions (e.g., ACKNOWLEDGE_SESSION_VIDEO, START_BREAK,
        END_BREAK) are intentionally excluded: they're invoked by the frontend
        on button clicks, never emitted by the LLM, and therefore have no
        entry in ACTION_TYPE_TO_MODEL.
        """
        action_values = [a.value for a in ActionType.llm_callable_actions()]
        model_cls = build_dynamic_response_format(action_values)
        self.assertIn("message", model_cls.model_fields)
        self.assertEqual(
            len(model_cls.model_fields), len(action_values) + 1
        )
