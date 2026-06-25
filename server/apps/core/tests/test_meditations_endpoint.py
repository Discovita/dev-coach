"""
Tests for the GET /api/v1/core/public/meditations endpoint.

Verifies public accessibility and that the env-driven feature flag flows
through from Django settings to the HTTP response.
"""

from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient


class MeditationsEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # trailing_slash=False on default_router
        self.url = "/api/v1/core/public/meditations"

    def test_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_accessible_without_authentication(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_response_has_expected_keys(self):
        response = self.client.get(self.url)
        self.assertEqual(set(response.data.keys()), {"enabled"})

    @override_settings(MEDITATIONS_ENABLED=True)
    def test_reflects_enabled_flag_when_on(self):
        response = self.client.get(self.url)
        self.assertTrue(response.data["enabled"])

    @override_settings(MEDITATIONS_ENABLED=False)
    def test_reflects_enabled_flag_when_off(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["enabled"])
        self.assertEqual(set(response.data.keys()), {"enabled"})

    def test_post_not_allowed(self):
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
