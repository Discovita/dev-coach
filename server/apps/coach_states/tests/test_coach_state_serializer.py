"""
Tests for CoachStateSerializer.

Verifies the serializer exposes the fields we expect over the API — in
particular that `shown_videos` is included so the frontend can derive
Watch vs Watch Again for session videos.
"""

from django.test import TestCase

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
