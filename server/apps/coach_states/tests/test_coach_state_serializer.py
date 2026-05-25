"""
Tests for CoachStateSerializer.

Verifies the serializer exposes the fields we expect over the API — in
particular that `shown_videos` is included so the frontend can derive
Watch vs Watch Again for session videos, and that `on_break` is derived
from the `Break` table on every read.
"""

from django.test import TestCase
from django.utils import timezone

from apps.coach_states.models import Break
from apps.coach_states.serializers import CoachStateSerializer
from apps.users.models import User


class CoachStateSerializerTests(TestCase):
    """Tests for CoachStateSerializer field exposure."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="serializer@example.com",
            password="testpass123",
        )
        # Signal auto-creates the CoachState
        self.coach_state = self.user.coach_state

    def test_serializer_includes_shown_videos(self):
        """Serialized output must include `shown_videos`."""
        data = CoachStateSerializer(self.coach_state).data
        self.assertIn("shown_videos", data)

    def test_serializer_shown_videos_defaults_to_empty_list(self):
        """A brand-new CoachState serializes `shown_videos` as []."""
        data = CoachStateSerializer(self.coach_state).data
        self.assertEqual(data["shown_videos"], [])

    def test_serializer_reflects_shown_videos_after_append(self):
        """Appended video keys appear in the serialized output."""
        self.coach_state.shown_videos = [
            "welcome_session_intro",
            "get_to_know_session_intro",
        ]
        self.coach_state.save()

        data = CoachStateSerializer(self.coach_state).data
        self.assertEqual(
            data["shown_videos"],
            ["welcome_session_intro", "get_to_know_session_intro"],
        )

    # ---- on_break derived field ------------------------------------------

    def test_user_state_on_break_false_when_no_break_rows(self):
        """No Break rows for the user → `on_break` is False."""
        data = CoachStateSerializer(self.coach_state).data
        self.assertIn("on_break", data)
        self.assertFalse(data["on_break"])

    def test_user_state_on_break_true_when_open_break_exists(self):
        """An open Break (ended_at IS NULL) → `on_break` is True."""
        Break.objects.create(
            user=self.user,
            triggered_by_session="get_to_know_session",
        )

        data = CoachStateSerializer(self.coach_state).data
        self.assertTrue(data["on_break"])

    def test_user_state_on_break_false_when_break_ended_at_set(self):
        """A closed Break (ended_at IS NOT NULL) → `on_break` is False."""
        Break.objects.create(
            user=self.user,
            triggered_by_session="get_to_know_session",
            ended_at=timezone.now(),
        )

        data = CoachStateSerializer(self.coach_state).data
        self.assertFalse(data["on_break"])

    def test_on_break_isolated_per_user(self):
        """User A's open break must not make user B `on_break`."""
        user_b = User.objects.create_user(
            email="other@example.com",
            password="testpass123",
        )

        Break.objects.create(
            user=self.user,
            triggered_by_session="get_to_know_session",
        )

        data_a = CoachStateSerializer(self.coach_state).data
        data_b = CoachStateSerializer(user_b.coach_state).data

        self.assertTrue(data_a["on_break"])
        self.assertFalse(data_b["on_break"])
