"""
Tests for the Coaching Phase Videos additions to `ActionType`.
"""

from django.test import TestCase

from enums.action_type import ActionType


class ActionTypeVideoActionsTests(TestCase):
    """The three user-button-only actions added for the videos feature."""

    def test_actiontype_has_acknowledge_session_video(self):
        self.assertEqual(
            ActionType.ACKNOWLEDGE_SESSION_VIDEO.value,
            "acknowledge_session_video",
        )

    def test_actiontype_has_start_break(self):
        self.assertEqual(ActionType.START_BREAK.value, "start_break")

    def test_actiontype_has_end_break(self):
        self.assertEqual(ActionType.END_BREAK.value, "end_break")

    def test_new_actions_have_labels(self):
        """All three new actions expose a human-readable label."""
        self.assertEqual(
            ActionType.ACKNOWLEDGE_SESSION_VIDEO.label,
            "Acknowledge Session Video",
        )
        self.assertEqual(ActionType.START_BREAK.label, "Start Break")
        self.assertEqual(ActionType.END_BREAK.label, "End Break")

    def test_new_actions_resolvable_by_from_string(self):
        """from_string accepts both the value and the enum name."""
        self.assertEqual(
            ActionType.from_string("acknowledge_session_video"),
            ActionType.ACKNOWLEDGE_SESSION_VIDEO,
        )
        self.assertEqual(
            ActionType.from_string("start_break"), ActionType.START_BREAK
        )
        self.assertEqual(
            ActionType.from_string("end_break"), ActionType.END_BREAK
        )
