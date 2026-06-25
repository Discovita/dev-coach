"""
Tests for the get_meditations function.

Verifies that the function reads Django settings and always returns the full
config shape regardless of whether the feature is enabled.
"""

from django.test import TestCase, override_settings

from apps.core.functions import get_meditations


class GetMeditationsTests(TestCase):
    def test_returns_full_shape(self):
        self.assertEqual(set(get_meditations().keys()), {"enabled"})

    @override_settings(MEDITATIONS_ENABLED=True)
    def test_reflects_enabled_true(self):
        self.assertTrue(get_meditations()["enabled"])

    @override_settings(MEDITATIONS_ENABLED=False)
    def test_reflects_enabled_false(self):
        self.assertFalse(get_meditations()["enabled"])
