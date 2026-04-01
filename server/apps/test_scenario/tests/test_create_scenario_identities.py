"""
Tests for create_scenario_identities function.
"""

from unittest.mock import patch

from django.test import TestCase

from apps.identities.models import Identity
from apps.test_scenario.utils import create_scenario_identities
from apps.test_scenario.models import TestScenario
from apps.users.models import User


def _make_scenario(name="Identity Scenario"):
    return TestScenario.objects.create(
        name=name,
        template={"user": {"first_name": "Test", "last_name": "User"}},
    )


class TestCreateScenarioIdentities(TestCase):
    """create_scenario_identities tests."""

    def setUp(self):
        self.scenario = _make_scenario()
        self.user = User.objects.create_user(
            email="create_id@example.com", password="testpass",
            test_scenario=self.scenario,
        )

    # ==================== Validation ====================

    def test_raises_when_user_has_no_pk(self):
        """Should raise ValueError when user has no valid PK."""
        from unittest.mock import MagicMock
        fake_user = MagicMock()
        fake_user.id = None
        template = {"identities": [{"name": "Explorer", "category": "PASSIONS"}]}
        with self.assertRaises(ValueError):
            create_scenario_identities(self.scenario, template, fake_user)

    # ==================== Creation ====================

    def test_creates_identities_from_template(self):
        """Should create one Identity per entry in the template."""
        template = {
            "identities": [
                {"name": "Explorer", "category": "PASSIONS"},
                {"name": "Creator", "category": "MONEY_MAKER"},
            ]
        }
        create_scenario_identities(self.scenario, template, self.user)
        count = Identity.objects.filter(
            user=self.user, test_scenario=self.scenario
        ).count()
        self.assertEqual(count, 2)

    def test_returns_name_keyed_mapping(self):
        """Should return a dict mapping identity name to Identity instance."""
        template = {
            "identities": [{"name": "Explorer", "category": "PASSIONS"}]
        }
        result = create_scenario_identities(self.scenario, template, self.user)
        self.assertIn("Explorer", result)
        self.assertIsInstance(result["Explorer"], Identity)

    def test_sets_optional_fields(self):
        """Should set optional fields from the template entry."""
        template = {
            "identities": [
                {
                    "name": "Explorer",
                    "category": "PASSIONS",
                    "state": "ACCEPTED",
                    "i_am_statement": "I am an explorer.",
                    "visualization": "A vivid scene.",
                    "notes": ["note1"],
                }
            ]
        }
        create_scenario_identities(self.scenario, template, self.user)
        identity = Identity.objects.get(
            user=self.user, test_scenario=self.scenario, name="Explorer"
        )
        self.assertEqual(identity.state, "ACCEPTED")
        self.assertEqual(identity.i_am_statement, "I am an explorer.")

    # ==================== Image handling ====================

    def test_skips_image_when_copy_fails(self):
        """Should create identity without image when copy_image_from_url returns None."""
        template = {
            "identities": [
                {
                    "name": "Explorer",
                    "category": "PASSIONS",
                    "image": "https://example.com/photo.jpg",
                }
            ]
        }
        with patch(
            "apps.test_scenario.utils.create_scenario_identities.copy_image_from_url",
            return_value=None,
        ):
            create_scenario_identities(self.scenario, template, self.user)
        identity = Identity.objects.get(
            user=self.user, test_scenario=self.scenario
        )
        self.assertFalse(bool(identity.image.name))

    # ==================== Idempotency ====================

    def test_deletes_existing_identities_before_creating(self):
        """Should delete previous identities for the same scenario/user."""
        template = {"identities": [{"name": "Explorer", "category": "PASSIONS"}]}
        create_scenario_identities(self.scenario, template, self.user)
        create_scenario_identities(self.scenario, template, self.user)
        count = Identity.objects.filter(
            user=self.user, test_scenario=self.scenario
        ).count()
        self.assertEqual(count, 1)
