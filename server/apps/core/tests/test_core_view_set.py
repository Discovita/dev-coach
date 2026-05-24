"""
Tests for apps.core.views.CoreViewSet.

Verifies the /api/v1/core/enums endpoint returns all expected enum groups
and requires authentication.
"""

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from conftest import create_test_user
from enums.action_type import ActionType
from enums.coaching_phase import CoachingPhase
from enums.context_keys import ContextKey
from enums.prompt_type import PromptType


class CoreViewSetEnumsEndpointTests(TestCase):
    """Tests for the GET /api/v1/core/enums endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_test_user()
        self.client.force_authenticate(user=self.user)

    def test_requires_authentication(self):
        """Should return 401 for unauthenticated requests."""
        anon_client = APIClient()
        response = anon_client.get("/api/v1/core/enums")
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_returns_200_for_authenticated_user(self):
        """Should return 200 for authenticated users."""
        response = self.client.get("/api/v1/core/enums")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_response_contains_all_enum_groups(self):
        """Response should contain all expected top-level enum groups."""
        response = self.client.get("/api/v1/core/enums")
        data = response.data

        expected_keys = [
            "coaching_phases",
            "allowed_actions",
            "context_keys",
            "prompt_types",
            "appearance",
        ]
        for key in expected_keys:
            self.assertIn(key, data, f"Missing enum group: {key}")

    def test_coaching_phases_has_correct_count(self):
        """Should return all CoachingPhase values."""
        response = self.client.get("/api/v1/core/enums")
        self.assertEqual(
            len(response.data["coaching_phases"]),
            len(CoachingPhase),
        )

    def test_allowed_actions_has_correct_count(self):
        """Should return all ActionType values."""
        response = self.client.get("/api/v1/core/enums")
        self.assertEqual(
            len(response.data["allowed_actions"]),
            len(ActionType),
        )

    def test_enum_items_have_value_and_label(self):
        """Each enum item should have 'value' and 'label' keys."""
        response = self.client.get("/api/v1/core/enums")
        for item in response.data["coaching_phases"]:
            self.assertIn("value", item)
            self.assertIn("label", item)

    def test_appearance_contains_all_subcategories(self):
        """Appearance group should have all expected subcategories."""
        response = self.client.get("/api/v1/core/enums")
        appearance = response.data["appearance"]

        expected_appearance_keys = [
            "genders",
            "skin_tones",
            "hair_colors",
            "eye_colors",
            "heights",
            "builds_male",
            "builds_female",
            "builds_neutral",
            "age_ranges",
        ]
        for key in expected_appearance_keys:
            self.assertIn(key, appearance, f"Missing appearance key: {key}")

    def test_appearance_items_are_non_empty(self):
        """Each appearance subcategory should have at least one entry."""
        response = self.client.get("/api/v1/core/enums")
        for key, items in response.data["appearance"].items():
            self.assertGreater(len(items), 0, f"Empty appearance group: {key}")

    def test_response_includes_component_types_group(self):
        """`component_types` group is exposed (added with the videos feature)."""
        response = self.client.get("/api/v1/core/enums")
        self.assertIn("component_types", response.data)

    def test_component_types_has_value_and_label(self):
        """Each component_types item must have value + label keys."""
        response = self.client.get("/api/v1/core/enums")
        for item in response.data["component_types"]:
            self.assertIn("value", item)
            self.assertIn("label", item)

    def test_enums_endpoint_response_includes_new_action_types(self):
        """The three Coaching Phase Videos actions appear in `allowed_actions`."""
        response = self.client.get("/api/v1/core/enums")
        values = {item["value"] for item in response.data["allowed_actions"]}
        self.assertIn("acknowledge_session_video", values)
        self.assertIn("start_break", values)
        self.assertIn("end_break", values)

    def test_enums_endpoint_response_includes_new_component_types(self):
        """The two Coaching Phase Videos components appear in `component_types`."""
        response = self.client.get("/api/v1/core/enums")
        values = {item["value"] for item in response.data["component_types"]}
        self.assertIn("session_video", values)
        self.assertIn("session_break", values)
