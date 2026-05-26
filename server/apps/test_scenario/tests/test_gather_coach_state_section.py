"""
Tests for gather_coach_state_section function.
"""

from django.test import TestCase

from apps.coach_states.models import CoachState
from apps.test_scenario.utils import gather_coach_state_section
from apps.users.models import User


class TestGatherCoachStateSection(TestCase):
    """gather_coach_state_section tests."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="gather_cs@example.com", password="testpass"
        )

    # ==================== No CoachState ====================

    def test_returns_none_when_no_coach_state(self):
        """Should return None if the user has no CoachState."""
        CoachState.objects.filter(user=self.user).delete()
        result = gather_coach_state_section(self.user)
        self.assertIsNone(result)

    # ==================== Basic fields ====================

    def test_returns_required_fields(self):
        """Should include the four required CoachState fields."""
        cs = CoachState.objects.get(user=self.user)
        cs.current_phase = "IDENTITY_BRAINSTORMING"
        cs.identity_focus = "PASSIONS"
        cs.who_you_are = ["Explorer"]
        cs.who_you_want_to_be = ["Visionary"]
        cs.save()

        result = gather_coach_state_section(self.user)

        self.assertIsNotNone(result)
        self.assertEqual(result["current_phase"], "IDENTITY_BRAINSTORMING")
        self.assertEqual(result["identity_focus"], "PASSIONS")
        self.assertEqual(result["who_you_are"], ["Explorer"])
        self.assertEqual(result["who_you_want_to_be"], ["Visionary"])

    # ==================== Optional fields ====================

    def test_includes_skipped_identity_categories_when_present(self):
        """Should include skipped_identity_categories when non-empty."""
        cs = CoachState.objects.get(user=self.user)
        cs.skipped_identity_categories = ["FAMILY"]
        cs.save()

        result = gather_coach_state_section(self.user)
        self.assertIn("skipped_identity_categories", result)
        self.assertEqual(result["skipped_identity_categories"], ["FAMILY"])

    def test_omits_skipped_identity_categories_when_empty(self):
        """Should omit skipped_identity_categories when empty."""
        cs = CoachState.objects.get(user=self.user)
        cs.skipped_identity_categories = []
        cs.save()

        result = gather_coach_state_section(self.user)
        self.assertNotIn("skipped_identity_categories", result)

    def test_includes_asked_questions_when_present(self):
        """Should include asked_questions when non-empty."""
        cs = CoachState.objects.get(user=self.user)
        cs.asked_questions = ["Q1"]
        cs.save()

        result = gather_coach_state_section(self.user)
        self.assertIn("asked_questions", result)

    def test_includes_metadata_when_present(self):
        """Should include metadata when non-empty."""
        cs = CoachState.objects.get(user=self.user)
        cs.metadata = {"key": "value"}
        cs.save()

        result = gather_coach_state_section(self.user)
        self.assertIn("metadata", result)
        self.assertEqual(result["metadata"], {"key": "value"})

    # ==================== Coaching Phase Videos ==================

    def test_includes_shown_videos_when_present(self):
        """Should include shown_videos when non-empty (PR 111)."""
        cs = CoachState.objects.get(user=self.user)
        cs.shown_videos = ["welcome_session_intro", "get_to_know_session_intro"]
        cs.save()

        result = gather_coach_state_section(self.user)
        self.assertIn("shown_videos", result)
        self.assertEqual(
            result["shown_videos"],
            ["welcome_session_intro", "get_to_know_session_intro"],
        )

    def test_omits_shown_videos_when_empty(self):
        """Should omit shown_videos when empty (matches optional-field convention)."""
        cs = CoachState.objects.get(user=self.user)
        cs.shown_videos = []
        cs.save()

        result = gather_coach_state_section(self.user)
        self.assertNotIn("shown_videos", result)
