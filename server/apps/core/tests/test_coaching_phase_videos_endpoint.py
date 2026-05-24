"""
Tests for the GET /api/v1/core/public/coaching-phase-videos endpoint.

Verifies public accessibility and that the feature flag flows through
from Django settings to the HTTP response.
"""

from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient


class CoachingPhaseVideosEndpointTests(TestCase):
    """Tests for the GET /api/v1/core/public/coaching-phase-videos endpoint."""

    def setUp(self):
        self.client = APIClient()
        # trailing_slash=False on default_router
        self.url = "/api/v1/core/public/coaching-phase-videos"

    def test_returns_200(self):
        """Should return 200 OK."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_accessible_without_authentication(self):
        """Should be publicly accessible — no auth required."""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_response_has_expected_keys(self):
        """Should return all documented keys."""
        response = self.client.get(self.url)
        self.assertEqual(set(response.data.keys()), {"enabled"})

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=True)
    def test_reflects_enabled_flag_when_on(self):
        """Should reflect COACHING_PHASE_VIDEOS_ENABLED=True in the response."""
        response = self.client.get(self.url)
        self.assertTrue(response.data["enabled"])

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=False)
    def test_reflects_enabled_flag_when_off(self):
        """Should still return full shape when the flag is off."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["enabled"])
        self.assertEqual(set(response.data.keys()), {"enabled"})

    def test_post_not_allowed(self):
        """Should reject POST — read-only endpoint."""
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
