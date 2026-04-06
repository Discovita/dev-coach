"""
Tests for build_user_template_section utility.
"""

from unittest.mock import MagicMock

from django.test import TestCase

from apps.test_scenario.utils import build_user_template_section


def _make_user(email="user@example.com", first_name="Jane", last_name="Doe"):
    """Return a simple mock user object."""
    user = MagicMock()
    user.email = email
    user.first_name = first_name
    user.last_name = last_name
    return user


class TestBuildUserTemplateSection(TestCase):
    """build_user_template_section tests."""

    # ==================== Basic output ====================

    def test_returns_dict_with_required_keys(self):
        """Should return a dict with email, first_name, and last_name."""
        user = _make_user()
        result = build_user_template_section(user)
        self.assertIn("email", result)
        self.assertIn("first_name", result)
        self.assertIn("last_name", result)

    def test_uses_user_email(self):
        """Should use the user's email address."""
        user = _make_user(email="test@example.com")
        result = build_user_template_section(user)
        self.assertEqual(result["email"], "test@example.com")

    # ==================== Name override logic ====================

    def test_override_first_name_takes_precedence(self):
        """Provided first_name should override the user's first_name."""
        user = _make_user(first_name="Jane")
        result = build_user_template_section(user, first_name="Alice")
        self.assertEqual(result["first_name"], "Alice")

    def test_override_last_name_takes_precedence(self):
        """Provided last_name should override the user's last_name."""
        user = _make_user(last_name="Doe")
        result = build_user_template_section(user, last_name="Smith")
        self.assertEqual(result["last_name"], "Smith")

    def test_falls_back_to_user_first_name_when_override_empty(self):
        """Should use user.first_name when override is an empty string."""
        user = _make_user(first_name="Jane")
        result = build_user_template_section(user, first_name="")
        self.assertEqual(result["first_name"], "Jane")

    def test_falls_back_to_user_last_name_when_override_empty(self):
        """Should use user.last_name when override is an empty string."""
        user = _make_user(last_name="Doe")
        result = build_user_template_section(user, last_name="")
        self.assertEqual(result["last_name"], "Doe")

    def test_strips_whitespace_from_override(self):
        """Should strip leading/trailing whitespace from overrides."""
        user = _make_user(first_name="Jane")
        result = build_user_template_section(user, first_name="  ")
        # "  ".strip() == "" so should fall back to user's name
        self.assertEqual(result["first_name"], "Jane")

    def test_defaults_to_test_when_no_first_name_anywhere(self):
        """Should default to 'Test' when override is empty and user has no first_name."""
        user = _make_user(first_name="")
        result = build_user_template_section(user, first_name="")
        self.assertEqual(result["first_name"], "Test")

    def test_defaults_to_user_when_no_last_name_anywhere(self):
        """Should default to 'User' when override is empty and user has no last_name."""
        user = _make_user(last_name="")
        result = build_user_template_section(user, last_name="")
        self.assertEqual(result["last_name"], "User")

    # ==================== No extra keys ====================

    def test_only_three_keys_returned(self):
        """Should return exactly three keys."""
        user = _make_user()
        result = build_user_template_section(user)
        self.assertEqual(set(result.keys()), {"email", "first_name", "last_name"})
