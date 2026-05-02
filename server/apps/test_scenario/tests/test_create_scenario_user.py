"""
Tests for create_scenario_user function.
"""

from django.test import TestCase

from apps.test_scenario.utils import create_scenario_user
from apps.test_scenario.models import TestScenario
from apps.users.models import User


def _make_scenario(name="Test Scenario"):
    return TestScenario.objects.create(
        name=name,
        template={"user": {"first_name": "Test", "last_name": "User"}},
    )


class TestCreateScenarioUser(TestCase):
    """create_scenario_user tests."""

    def setUp(self):
        self.scenario = _make_scenario()

    # ==================== Success cases ====================

    def test_creates_user_and_returns_tuple(self):
        """Should return a (User, email) tuple."""
        template = {"user": {"first_name": "Alice", "last_name": "Smith"}}
        user, email = create_scenario_user(self.scenario, template)
        self.assertIsNotNone(user)
        self.assertIsNotNone(email)
        self.assertIsInstance(email, str)

    def test_created_user_has_test_scenario_set(self):
        """Created user should be linked to the scenario."""
        template = {"user": {"first_name": "Alice", "last_name": "Smith"}}
        user, _ = create_scenario_user(self.scenario, template)
        self.assertEqual(user.test_scenario, self.scenario)

    def test_uses_template_email_when_unique(self):
        """Should use the template email when it is not already in use."""
        template = {
            "user": {
                "email": "unique_create@example.com",
                "first_name": "Alice",
                "last_name": "Smith",
            }
        }
        user, email = create_scenario_user(self.scenario, template)
        self.assertEqual(email, "unique_create@example.com")
        self.assertEqual(user.email, "unique_create@example.com")

    def test_generates_unique_email_when_template_email_taken(self):
        """Should generate a unique email when the template email already exists."""
        User.objects.create_user(email="taken@example.com", password="x")
        template = {
            "user": {
                "email": "taken@example.com",
                "first_name": "Alice",
                "last_name": "Smith",
            }
        }
        _, email = create_scenario_user(self.scenario, template)
        self.assertIn("@testscenario.com", email)

    def test_generates_unique_email_when_no_template_email(self):
        """Should generate a unique email when the template has no email field."""
        template = {"user": {"first_name": "Alice", "last_name": "Smith"}}
        _, email = create_scenario_user(self.scenario, template)
        self.assertIn("@testscenario.com", email)

    def test_password_is_set_correctly(self):
        """Created user should be authenticatable with the default password."""
        template = {"user": {"first_name": "Alice", "last_name": "Smith"}}
        user, _ = create_scenario_user(self.scenario, template)
        self.assertTrue(user.check_password("Coach123!"))

    # ==================== Idempotency ====================

    def test_deletes_existing_user_before_creating(self):
        """Calling a second time should delete the old user and create a fresh one."""
        template = {"user": {"first_name": "Alice", "last_name": "Smith"}}
        user1, _ = create_scenario_user(self.scenario, template)
        user2, _ = create_scenario_user(self.scenario, template)
        self.assertFalse(User.objects.filter(pk=user1.pk).exists())
        self.assertTrue(User.objects.filter(pk=user2.pk).exists())

    # ==================== Field stripping ====================

    def test_strips_reserved_fields_from_template(self):
        """Should silently drop reserved fields like 'password', 'id', 'last_login'."""
        template = {
            "user": {
                "first_name": "Alice",
                "last_name": "Smith",
                "password": "should-be-ignored",
                "id": "fake-uuid",
                "last_login": "2024-01-01T00:00:00Z",
            }
        }
        user, _ = create_scenario_user(self.scenario, template)
        self.assertIsNotNone(user)
