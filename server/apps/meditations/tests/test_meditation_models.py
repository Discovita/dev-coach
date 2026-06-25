"""
Tests for the meditation models (Meditation / MeditationSegment /
MeditationAsset): defaults, relationships, and the uniqueness invariants.
"""

from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.identities.models import Identity
from apps.meditations.models import Meditation, MeditationAsset, MeditationSegment
from apps.users.models import User
from enums.meditation import (
    MeditationAssetKind,
    MeditationAssetStatus,
    MeditationStatus,
)


def _make_user(email="med@example.com"):
    return User.objects.create_user(email=email, password="testpass123")


class MeditationModelTests(TestCase):
    def setUp(self):
        self.user = _make_user()

    def test_defaults(self):
        med = Meditation.objects.create(user=self.user)
        self.assertEqual(med.status, MeditationStatus.PENDING)
        self.assertEqual(med.final_video_s3_key, "")
        self.assertIsNotNone(med.id)

    def test_related_name(self):
        Meditation.objects.create(user=self.user)
        self.assertEqual(self.user.meditations.count(), 1)


class MeditationSegmentModelTests(TestCase):
    def setUp(self):
        self.user = _make_user()
        self.med = Meditation.objects.create(user=self.user)
        self.identity = Identity.objects.create(user=self.user, name="Creator")

    def test_create_segment(self):
        seg = MeditationSegment.objects.create(
            meditation=self.med, identity=self.identity, order=2
        )
        self.assertEqual(self.med.segments.count(), 1)
        self.assertEqual(seg.current_video_prompt, "")
        self.assertEqual(seg.current_audio_script, "")

    def test_unique_meditation_identity(self):
        MeditationSegment.objects.create(meditation=self.med, identity=self.identity)
        with self.assertRaises(IntegrityError):
            MeditationSegment.objects.create(
                meditation=self.med, identity=self.identity
            )


class MeditationAssetModelTests(TestCase):
    def setUp(self):
        self.user = _make_user()
        self.med = Meditation.objects.create(user=self.user)
        self.identity = Identity.objects.create(user=self.user, name="Creator")
        self.segment = MeditationSegment.objects.create(
            meditation=self.med, identity=self.identity
        )

    def test_defaults(self):
        asset = MeditationAsset.objects.create(
            segment=self.segment, kind=MeditationAssetKind.VIDEO
        )
        self.assertEqual(asset.status, MeditationAssetStatus.QUEUED)
        self.assertEqual(asset.version, 1)
        self.assertFalse(asset.is_active)
        self.assertEqual(asset.error_code, "")

    def test_unique_version_per_kind(self):
        MeditationAsset.objects.create(
            segment=self.segment, kind=MeditationAssetKind.VIDEO, version=1
        )
        with self.assertRaises(IntegrityError):
            MeditationAsset.objects.create(
                segment=self.segment, kind=MeditationAssetKind.VIDEO, version=1
            )

    def test_only_one_active_per_segment_kind(self):
        MeditationAsset.objects.create(
            segment=self.segment,
            kind=MeditationAssetKind.VIDEO,
            version=1,
            is_active=True,
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                MeditationAsset.objects.create(
                    segment=self.segment,
                    kind=MeditationAssetKind.VIDEO,
                    version=2,
                    is_active=True,
                )

    def test_active_allowed_across_different_kinds(self):
        MeditationAsset.objects.create(
            segment=self.segment,
            kind=MeditationAssetKind.VIDEO,
            version=1,
            is_active=True,
        )
        # An active audio asset for the same segment is fine — different kind.
        audio = MeditationAsset.objects.create(
            segment=self.segment,
            kind=MeditationAssetKind.AUDIO,
            version=1,
            is_active=True,
        )
        self.assertTrue(audio.is_active)
