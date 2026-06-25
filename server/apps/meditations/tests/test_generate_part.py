"""
Tests for the two-step generation flow: create_pending_asset (synchronous,
QUEUED) and generate_asset (the task body — provider → S3 → READY/FAILED). The
provider call and storage are mocked (providers are covered in services/media
tests).
"""

from unittest.mock import patch

from django.test import TestCase

from apps.meditations.models import Meditation, MeditationAsset, MeditationSegment
from apps.meditations.services import create_pending_asset, generate_asset
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


class GenerationFlowTests(TestCase):
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

    def test_create_pending_asset(self):
        asset = create_pending_asset(self.segment, MeditationAssetKind.VIDEO)
        self.assertEqual(asset.status, MeditationAssetStatus.QUEUED)
        self.assertEqual(asset.version, 1)
        self.assertEqual(asset.prompt_snapshot, "serene push-in")
        self.assertFalse(asset.is_active)
        self.med.refresh_from_db()
        self.assertEqual(self.med.status, MeditationStatus.GENERATING_PARTS)

    def test_create_pending_audio_uses_script(self):
        asset = create_pending_asset(self.segment, MeditationAssetKind.AUDIO)
        self.assertEqual(asset.prompt_snapshot, "I am calm.")

    @patch("apps.meditations.services.generate_part.default_storage")
    @patch("apps.meditations.services.generate_part._run_provider")
    def test_generate_asset_success(self, mock_run, mock_storage):
        mock_run.return_value = _result("video")
        mock_storage.save.return_value = "meditations/k/video_v1.mp4"
        pending = create_pending_asset(self.segment, MeditationAssetKind.VIDEO)

        asset = generate_asset(str(pending.id))

        self.assertEqual(asset.status, MeditationAssetStatus.READY)
        self.assertEqual(asset.s3_key, "meditations/k/video_v1.mp4")
        self.assertTrue(asset.is_active)
        # The provider is called with the snapshotted prompt.
        self.assertEqual(mock_run.call_args.args[2], "serene push-in")

    @patch("apps.meditations.services.generate_part.default_storage")
    @patch("apps.meditations.services.generate_part._run_provider")
    def test_new_version_demotes_prior_active(self, mock_run, mock_storage):
        mock_run.return_value = _result("video")
        mock_storage.save.side_effect = ["k/v1.mp4", "k/v2.mp4"]

        first = generate_asset(
            str(create_pending_asset(self.segment, MeditationAssetKind.VIDEO).id)
        )
        second = generate_asset(
            str(create_pending_asset(self.segment, MeditationAssetKind.VIDEO).id)
        )

        first.refresh_from_db()
        self.assertFalse(first.is_active)
        self.assertTrue(second.is_active)
        self.assertEqual(second.version, 2)
        active = MeditationAsset.objects.filter(
            segment=self.segment, kind=MeditationAssetKind.VIDEO, is_active=True
        )
        self.assertEqual(active.count(), 1)

    @patch("apps.meditations.services.generate_part.default_storage")
    @patch("apps.meditations.services.generate_part._run_provider")
    def test_provider_failure_marks_failed(self, mock_run, mock_storage):
        mock_run.side_effect = MediaGenerationError(
            "blocked", MediaGenerationError.SAFETY_BLOCK
        )
        pending = create_pending_asset(self.segment, MeditationAssetKind.VIDEO)

        asset = generate_asset(str(pending.id))

        self.assertEqual(asset.status, MeditationAssetStatus.FAILED)
        self.assertEqual(asset.error_code, MediaGenerationError.SAFETY_BLOCK)
        self.assertFalse(asset.is_active)
        mock_storage.save.assert_not_called()
