"""
Tests for create_scenario_user_notes function.
"""

from django.test import TestCase

from apps.test_scenario.utils import create_scenario_user_notes
from apps.test_scenario.models import TestScenario
from apps.user_notes.models import UserNote
from apps.users.models import User


def _make_scenario(name="Notes Scenario"):
    return TestScenario.objects.create(
        name=name,
        template={"user": {"first_name": "Test", "last_name": "User"}},
    )


class TestCreateScenarioUserNotes(TestCase):
    """create_scenario_user_notes tests."""

    def setUp(self):
        self.scenario = _make_scenario()
        self.user = User.objects.create_user(
            email="create_un@example.com", password="testpass",
            test_scenario=self.scenario,
        )

    # ==================== Creation ====================

    def test_creates_notes_from_template(self):
        """Should create one UserNote per entry in the template."""
        template = {
            "user_notes": [
                {"note": "First note"},
                {"note": "Second note"},
            ]
        }
        create_scenario_user_notes(self.scenario, template, self.user)
        count = UserNote.objects.filter(
            user=self.user, test_scenario=self.scenario
        ).count()
        self.assertEqual(count, 2)

    def test_note_content_matches_template(self):
        """Created notes should have the content from the template."""
        template = {"user_notes": [{"note": "Remember this"}]}
        create_scenario_user_notes(self.scenario, template, self.user)
        note = UserNote.objects.get(user=self.user, test_scenario=self.scenario)
        self.assertEqual(note.note, "Remember this")

    def test_returns_none(self):
        """Should return None (no return value)."""
        template = {"user_notes": [{"note": "x"}]}
        result = create_scenario_user_notes(self.scenario, template, self.user)
        self.assertIsNone(result)

    # ==================== Idempotency ====================

    def test_deletes_existing_notes_before_creating(self):
        """Should delete previous notes for the same scenario/user before re-creating."""
        template = {"user_notes": [{"note": "Note"}]}
        create_scenario_user_notes(self.scenario, template, self.user)
        create_scenario_user_notes(self.scenario, template, self.user)
        count = UserNote.objects.filter(
            user=self.user, test_scenario=self.scenario
        ).count()
        self.assertEqual(count, 1)
