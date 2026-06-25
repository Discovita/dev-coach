"""
Tests for create_meditation_for_user: eligible-identity selection, ordering,
and per-segment prompt/script seeding.

Relies on the seeded VIDEO_GENERATION prompt (migration
prompts/0020_seed_video_generation_prompt).
"""

from django.test import TestCase

from apps.meditations.models import Meditation
from apps.meditations.services import create_meditation_for_user
from conftest import create_test_identity, create_test_user


class CreateMeditationTests(TestCase):
    def setUp(self):
        self.user = create_test_user(email="med-create@example.com")

    def _eligible(self, name, order, i_am="I am whole."):
        return create_test_identity(
            self.user,
            name=name,
            order=order,
            i_am_statement=i_am,
            image=f"identities/{name}.png",
        )

    def test_includes_only_eligible_identities(self):
        self._eligible("Creator", order=1)
        # No image → excluded.
        create_test_identity(
            self.user, name="NoImage", order=2, i_am_statement="I am here."
        )
        # No i_am_statement → excluded.
        create_test_identity(
            self.user, name="NoStatement", order=3, image="identities/x.png"
        )

        meditation = create_meditation_for_user(self.user)

        self.assertEqual(meditation.segments.count(), 1)
        self.assertEqual(meditation.segments.first().identity.name, "Creator")

    def test_segments_ordered_by_identity_order(self):
        self._eligible("Third", order=30)
        self._eligible("First", order=10)
        self._eligible("Second", order=20)

        meditation = create_meditation_for_user(self.user)
        names = [s.identity.name for s in meditation.segments.all()]
        self.assertEqual(names, ["First", "Second", "Third"])

    def test_segment_seeded_with_script_and_prompt(self):
        self._eligible("Creator", order=1, i_am="I am unstoppable.")
        meditation = create_meditation_for_user(self.user)
        seg = meditation.segments.first()

        self.assertEqual(seg.current_audio_script, "I am unstoppable.")
        # The video prompt is the formatted template — non-empty and contains
        # the identity context.
        self.assertTrue(seg.current_video_prompt)
        self.assertIn("Creator", seg.current_video_prompt)

    def test_creates_pending_meditation(self):
        self._eligible("Creator", order=1)
        meditation = create_meditation_for_user(self.user)
        self.assertEqual(Meditation.objects.count(), 1)
        self.assertEqual(meditation.status, "PENDING")
