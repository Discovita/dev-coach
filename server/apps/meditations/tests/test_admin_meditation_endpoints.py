"""
Tests for the AdminMeditationViewSet endpoints under /api/v1/admin/meditations.
"""

from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.meditations.models import Meditation, MeditationAsset, MeditationSegment
from conftest import create_test_identity, create_test_user
from enums.meditation import MeditationAssetKind


class AdminMeditationEndpointTests(TestCase):
    def setUp(self):
        self.admin = create_test_user(email="admin@example.com", is_staff=True)
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)
        self.target = create_test_user(email="target@example.com")
        self.identity = create_test_identity(
            self.target,
            name="Creator",
            i_am_statement="I am bold.",
            image="identities/c.png",
        )

    def test_requires_admin(self):
        non_admin = create_test_user(email="plain@example.com")
        client = APIClient()
        client.force_authenticate(user=non_admin)
        response = client.get("/api/v1/admin/meditations")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_for_user(self):
        response = self.client.post(
            "/api/v1/admin/meditations/create-for-user",
            {"user_id": str(self.target.id)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["segments"]), 1)
        self.assertEqual(Meditation.objects.count(), 1)

    def test_create_for_user_requires_user_id(self):
        response = self.client.post(
            "/api/v1/admin/meditations/create-for-user", {}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_and_retrieve(self):
        med = Meditation.objects.create(user=self.target)
        list_resp = self.client.get("/api/v1/admin/meditations")
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_resp.data), 1)

        detail_resp = self.client.get(f"/api/v1/admin/meditations/{med.id}")
        self.assertEqual(detail_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_resp.data["id"], str(med.id))

    def test_list_filters_by_status(self):
        Meditation.objects.create(user=self.target, status="PENDING")
        Meditation.objects.create(user=self.target, status="COMPLETE")
        resp = self.client.get("/api/v1/admin/meditations?status=COMPLETE")
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["status"], "COMPLETE")

    @patch(
        "apps.meditations.views.admin_meditation_view_set.generate_segment_part_task"
    )
    def test_generate_part_enqueues_task(self, mock_task):
        med = Meditation.objects.create(user=self.target)
        segment = MeditationSegment.objects.create(
            meditation=med, identity=self.identity, order=0
        )
        response = self.client.post(
            "/api/v1/admin/meditations/generate-part",
            {"segment_id": str(segment.id), "kind": MeditationAssetKind.VIDEO},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        mock_task.delay_on_commit.assert_called_once_with(
            str(segment.id), MeditationAssetKind.VIDEO
        )

    def test_generate_part_rejects_bad_kind(self):
        med = Meditation.objects.create(user=self.target)
        segment = MeditationSegment.objects.create(
            meditation=med, identity=self.identity, order=0
        )
        response = self.client.post(
            "/api/v1/admin/meditations/generate-part",
            {"segment_id": str(segment.id), "kind": "GIF"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_set_active(self):
        med = Meditation.objects.create(user=self.target)
        segment = MeditationSegment.objects.create(
            meditation=med, identity=self.identity, order=0
        )
        a1 = MeditationAsset.objects.create(
            segment=segment, kind=MeditationAssetKind.VIDEO, version=1, is_active=True
        )
        a2 = MeditationAsset.objects.create(
            segment=segment, kind=MeditationAssetKind.VIDEO, version=2, is_active=False
        )
        response = self.client.post(
            "/api/v1/admin/meditations/set-active",
            {"asset_id": str(a2.id)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        a1.refresh_from_db()
        a2.refresh_from_db()
        self.assertFalse(a1.is_active)
        self.assertTrue(a2.is_active)

    def test_update_segment(self):
        med = Meditation.objects.create(user=self.target)
        segment = MeditationSegment.objects.create(
            meditation=med, identity=self.identity, order=0
        )
        response = self.client.patch(
            "/api/v1/admin/meditations/update-segment",
            {
                "segment_id": str(segment.id),
                "video_prompt": "new prompt",
                "audio_script": "I am new.",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        segment.refresh_from_db()
        self.assertEqual(segment.current_video_prompt, "new prompt")
        self.assertEqual(segment.current_audio_script, "I am new.")
