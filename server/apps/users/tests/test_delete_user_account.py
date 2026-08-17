"""
Tests for `delete_user_account` and the media cleanup it performs.

Storage is mocked throughout — these assert which keys are handed to the
storage backend, not that S3 accepted them.
"""

from unittest.mock import patch

from django.test import TestCase

from apps.identities.models import Identity
from apps.meditations.models import Meditation, MeditationAsset, MeditationSegment
from apps.reference_images.models import ReferenceImage
from apps.users.functions import delete_user_account
from apps.users.functions.admin.delete_user_media import collect_user_media_keys
from apps.users.models import User
from enums.meditation import MeditationAssetKind

STORAGE = "apps.users.functions.admin.delete_user_media.default_storage"


class CollectUserMediaKeysTests(TestCase):
    """Every storage key a user owns is found, and nobody else's is."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="target@example.com",
            password="testpass123",
        )
        self.identity = Identity.objects.create(user=self.user, name="Runner")

    def _make_meditation(self, user: User, **kwargs) -> Meditation:
        return Meditation.objects.create(user=user, **kwargs)

    def _make_asset(self, meditation: Meditation, s3_key: str, version: int = 1):
        segment, _ = MeditationSegment.objects.get_or_create(
            meditation=meditation,
            identity=self.identity,
            defaults={"order": 0},
        )
        return MeditationAsset.objects.create(
            segment=segment,
            kind=MeditationAssetKind.VIDEO,
            version=version,
            s3_key=s3_key,
        )

    def test_collects_every_asset_version_not_just_the_active_one(self):
        meditation = self._make_meditation(self.user)
        self._make_asset(meditation, "media/v1.mp4", version=1)
        self._make_asset(meditation, "media/v2.mp4", version=2)

        keys = collect_user_media_keys(self.user)

        self.assertIn("media/v1.mp4", keys)
        self.assertIn("media/v2.mp4", keys)

    def test_collects_the_assembled_final_video(self):
        self._make_meditation(self.user, final_video_s3_key="media/final.mp4")

        self.assertIn("media/final.mp4", collect_user_media_keys(self.user))

    def test_collects_image_files(self):
        self.identity.image = "media/identity.jpg"
        self.identity.save(update_fields=["image"])
        ReferenceImage.objects.create(
            user=self.user,
            order=0,
            image="media/reference.jpg",
        )

        keys = collect_user_media_keys(self.user)

        self.assertIn("media/identity.jpg", keys)
        self.assertIn("media/reference.jpg", keys)

    def test_skips_empty_keys(self):
        # A queued asset has no s3_key yet, and identities may have no image.
        meditation = self._make_meditation(self.user, final_video_s3_key="")
        self._make_asset(meditation, "")

        self.assertEqual(collect_user_media_keys(self.user), [])

    def test_ignores_another_users_media(self):
        other = User.objects.create_user(
            email="other@example.com",
            password="testpass123",
        )
        other_identity = Identity.objects.create(user=other, name="Theirs")
        other_meditation = Meditation.objects.create(
            user=other,
            final_video_s3_key="media/theirs.mp4",
        )
        other_segment = MeditationSegment.objects.create(
            meditation=other_meditation,
            identity=other_identity,
            order=0,
        )
        MeditationAsset.objects.create(
            segment=other_segment,
            kind=MeditationAssetKind.VIDEO,
            version=1,
            s3_key="media/their-asset.mp4",
        )

        self.assertEqual(collect_user_media_keys(self.user), [])

    def test_deduplicates_repeated_keys(self):
        meditation = self._make_meditation(
            self.user,
            final_video_s3_key="media/same.mp4",
        )
        self._make_asset(meditation, "media/same.mp4")

        self.assertEqual(collect_user_media_keys(self.user), ["media/same.mp4"])


class DeleteUserAccountTests(TestCase):
    """The account delete removes rows and the files they named."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="target@example.com",
            password="testpass123",
        )

    def test_deletes_the_users_storage_objects(self):
        Meditation.objects.create(user=self.user, final_video_s3_key="media/final.mp4")

        with patch(STORAGE) as storage:
            delete_user_account(self.user)

        storage.delete.assert_called_once_with("media/final.mp4")
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

    def test_a_storage_failure_does_not_undo_the_delete(self):
        """Rows are already gone; an S3 error leaves an orphan, not an exception."""
        Meditation.objects.create(user=self.user, final_video_s3_key="media/final.mp4")

        with patch(STORAGE) as storage:
            storage.delete.side_effect = Exception("S3 unavailable")
            delete_user_account(self.user)

        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

    def test_one_bad_key_does_not_block_the_rest(self):
        Meditation.objects.create(user=self.user, final_video_s3_key="media/first.mp4")
        Meditation.objects.create(user=self.user, final_video_s3_key="media/second.mp4")

        with patch(STORAGE) as storage:
            storage.delete.side_effect = [Exception("S3 unavailable"), None]
            delete_user_account(self.user)

        self.assertEqual(storage.delete.call_count, 2)

    def test_user_with_no_media_deletes_cleanly(self):
        with patch(STORAGE) as storage:
            delete_user_account(self.user)

        storage.delete.assert_not_called()
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())
