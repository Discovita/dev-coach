"""
Tests for the get_coaching_phase_videos function.

Verifies that the function reads Django settings and always returns the
full config shape regardless of whether the feature is enabled.
"""

from django.test import TestCase, override_settings

from apps.core.functions import get_coaching_phase_videos


class GetCoachingPhaseVideosTests(TestCase):
    """Tests for the get_coaching_phase_videos function."""

    def test_returns_full_shape(self):
        """Should return every documented key."""
        result = get_coaching_phase_videos()
        self.assertEqual(set(result.keys()), {"enabled"})

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=True)
    def test_reflects_enabled_true(self):
        """Should pass through the feature flag when on."""
        self.assertTrue(get_coaching_phase_videos()["enabled"])

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=False)
    def test_reflects_enabled_false(self):
        """Should pass through the feature flag when off."""
        self.assertFalse(get_coaching_phase_videos()["enabled"])

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=False)
    def test_returns_full_shape_even_when_disabled(self):
        """Shape doesn't shrink based on flag."""
        result = get_coaching_phase_videos()
        self.assertEqual(set(result.keys()), {"enabled"})
