"""
Tests for gather_breaks_section function (Coaching Phase Videos PR 111).
"""

from django.test import TestCase
from django.utils import timezone

from apps.coach_states.models import Break
from apps.test_scenario.utils import gather_breaks_section
from conftest import create_test_chat_message, create_test_user
from enums.message_role import MessageRole


class TestGatherBreaksSection(TestCase):
    """gather_breaks_section tests."""

    def setUp(self):
        self.user = create_test_user()

    def test_returns_empty_list_when_no_breaks(self):
        """Should return an empty list when the user has no Break rows."""
        result = gather_breaks_section(self.user)
        self.assertEqual(result, [])

    def test_returns_open_break(self):
        """Open breaks should be captured with `ended_at` absent."""
        Break.objects.create(
            user=self.user,
            triggered_by_session="get_to_know_session",
        )

        result = gather_breaks_section(self.user)

        self.assertEqual(len(result), 1)
        entry = result[0]
        self.assertEqual(entry["triggered_by_session"], "get_to_know_session")
        self.assertIn("started_at", entry)
        self.assertNotIn("ended_at", entry)

    def test_returns_closed_break(self):
        """Closed breaks should include both `started_at` and `ended_at`."""
        now = timezone.now()
        Break.objects.create(
            user=self.user,
            triggered_by_session="brainstorming_session",
            ended_at=now,
        )

        result = gather_breaks_section(self.user)

        self.assertEqual(len(result), 1)
        entry = result[0]
        self.assertIn("started_at", entry)
        self.assertIn("ended_at", entry)

    def test_includes_original_coach_message_id_when_linked(self):
        """The `coach_message` FK should be captured as `original_coach_message_id`."""
        coach_msg = create_test_chat_message(
            self.user, role=MessageRole.COACH, content="Take a break"
        )
        Break.objects.create(
            user=self.user,
            triggered_by_session="commitment_session",
            coach_message=coach_msg,
        )

        result = gather_breaks_section(self.user)

        self.assertEqual(result[0]["original_coach_message_id"], str(coach_msg.id))

    def test_omits_coach_message_id_when_unlinked(self):
        """Breaks with no coach_message should omit the field."""
        Break.objects.create(
            user=self.user,
            triggered_by_session="i_am_session",
        )

        result = gather_breaks_section(self.user)
        self.assertNotIn("original_coach_message_id", result[0])

    def test_returns_multiple_breaks_oldest_first(self):
        """Multiple Break rows should be returned in started_at order."""
        first = Break.objects.create(
            user=self.user, triggered_by_session="get_to_know_session"
        )
        second = Break.objects.create(
            user=self.user, triggered_by_session="brainstorming_session"
        )

        result = gather_breaks_section(self.user)

        self.assertEqual(len(result), 2)
        # `started_at` is auto_now_add so DB write order == time order.
        self.assertEqual(result[0]["triggered_by_session"], first.triggered_by_session)
        self.assertEqual(result[1]["triggered_by_session"], second.triggered_by_session)

    def test_isolates_per_user(self):
        """Should only gather breaks belonging to the given user."""
        other = create_test_user(email="other@example.com")
        Break.objects.create(user=other, triggered_by_session="get_to_know_session")
        Break.objects.create(user=self.user, triggered_by_session="brainstorming_session")

        result = gather_breaks_section(self.user)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["triggered_by_session"], "brainstorming_session")
