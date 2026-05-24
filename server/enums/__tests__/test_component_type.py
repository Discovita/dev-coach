"""
Tests for the Coaching Phase Videos additions to `ComponentType`.
"""

from django.test import TestCase

from enums.component_type import ComponentType


class ComponentTypeVideoComponentsTests(TestCase):
    """The two new component types added for the videos feature."""

    def test_componenttype_has_session_video(self):
        self.assertEqual(ComponentType.SESSION_VIDEO.value, "session_video")

    def test_componenttype_has_session_break(self):
        self.assertEqual(ComponentType.SESSION_BREAK.value, "session_break")

    def test_new_components_have_labels(self):
        self.assertEqual(ComponentType.SESSION_VIDEO.label, "Session Video")
        self.assertEqual(ComponentType.SESSION_BREAK.label, "Session Break")

    def test_new_components_resolvable_by_from_string(self):
        self.assertEqual(
            ComponentType.from_string("session_video"),
            ComponentType.SESSION_VIDEO,
        )
        self.assertEqual(
            ComponentType.from_string("session_break"),
            ComponentType.SESSION_BREAK,
        )
