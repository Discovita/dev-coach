"""
Tests for generate_segment_part: versioned asset creation, S3 upload, active
promotion/demotion, and failure handling. The provider call and storage are
mocked (the providers themselves are covered in services/media tests).
"""

from unittest.mock import patch

from django.test import TestCase

from apps.meditations.models import Meditation, MeditationAsset, MeditationSegment
from apps.meditations.services import generate_segment_part
from conftest import create_test_identity, create_test_user
from enums.meditation import (
    MeditationAssetKind,
    MeditationAssetStatus,
    MeditationStatus,
)
from services.media import MediaGenerationError, MediaResult


def _result(kind="video"):
    return MediaResult(
        data=b"BYTES",
        mime_type="video/mp4" if kind == "video" else "audio/wav",
        provider="GOOGLE_VEO" if kind == "video" else "GEMINI_TTS",
        model="test-model",
    )


class GenerateSegmentPartTests(TestCase):
    def setUp(self):
        self.user = create_test_user(email="gen@example.com")
        self.identity = create_test_identity(
            self.user, name="Creator", i_am_statement="I am calm.", image="x.png"
        )
        self.med = Meditation.objects.create(user=self.user)
        self.segment = MeditationSegment.objects.create(
            meditation=self.med,
            identity=self.identity,
            order=0,
            current_video_prompt="serene push-in",
            current_audio_script="I am calm.",
        )

    @patch("apps.meditations.services.generate_part.default_storage")
    @patch("apps.meditations.services.generate_part._run_provider")
    def test_video_success(self, mock_run, mock_storage):
        mock_run.return_value = _result("video")
        mock_storage.save.return_value = "meditations/k/video_v1.mp4"

        asset = generate_segment_part(str(self.segment.id), MeditationAssetKind.VIDEO)

        self.assertEqual(asset.status, MeditationAssetStatus.READY)
        self.assertEqual(asset.s3_key, "meditations/k/video_v1.mp4")
        self.assertTrue(asset.is_active)
        self.assertEqual(asset.version, 1)
        self.assertEqual(asset.prompt_snapshot, "serene push-in")
        self.med.refresh_from_db()
        self.assertEqual(self.med.status, MeditationStatus.GENERATING_PARTS)

    @patch("apps.meditations.services.generate_part.default_storage")
    @patch("apps.meditations.services.generate_part._run_provider")
    def test_audio_uses_script_snapshot(self, mock_run, mock_storage):
        mock_run.return_value = _result("audio")
        mock_storage.save.return_value = "meditations/k/audio_v1.wav"

        asset = generate_segment_part(str(self.segment.id), MeditationAssetKind.AUDIO)
        self.assertEqual(asset.prompt_snapshot, "I am calm.")
        self.assertEqual(asset.kind, MeditationAssetKind.AUDIO)

    @patch("apps.meditations.services.generate_part.default_storage")
    @patch("apps.meditations.services.generate_part._run_provider")
    def test_new_version_demotes_prior_active(self, mock_run, mock_storage):
        mock_run.return_value = _result("video")
        mock_storage.save.side_effect = ["k/v1.mp4", "k/v2.mp4"]

        first = generate_segment_part(str(self.segment.id), MeditationAssetKind.VIDEO)
        second = generate_segment_part(str(self.segment.id), MeditationAssetKind.VIDEO)

        first.refresh_from_db()
        self.assertFalse(first.is_active)
        self.assertTrue(second.is_active)
        self.assertEqual(second.version, 2)
        # Exactly one active video asset.
        active = MeditationAsset.objects.filter(
            segment=self.segment, kind=MeditationAssetKind.VIDEO, is_active=True
        )
        self.assertEqual(active.count(), 1)

    @patch("apps.meditations.services.generate_part.default_storage")
    @patch("apps.meditations.services.generate_part._run_provider")
    def test_provider_failure_marks_asset_failed(self, mock_run, mock_storage):
        mock_run.side_effect = MediaGenerationError(
            "blocked", MediaGenerationError.SAFETY_BLOCK
        )

        asset = generate_segment_part(str(self.segment.id), MeditationAssetKind.VIDEO)

        self.assertEqual(asset.status, MeditationAssetStatus.FAILED)
        self.assertEqual(asset.error_code, MediaGenerationError.SAFETY_BLOCK)
        self.assertFalse(asset.is_active)
        mock_storage.save.assert_not_called()
