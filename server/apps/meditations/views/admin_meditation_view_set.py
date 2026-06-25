"""
Admin Meditation ViewSet

Admin-only endpoints driving the meditations QC pipeline:
- GET  /api/v1/admin/meditations                 → list (optional ?status=)
- GET  /api/v1/admin/meditations/{id}            → detail (segments + assets)
- POST /api/v1/admin/meditations/create-for-user → build a meditation for a user
- POST /api/v1/admin/meditations/generate-part   → enqueue video/audio gen
- POST /api/v1/admin/meditations/set-active      → choose an asset version
- PATCH /api/v1/admin/meditations/update-segment → edit a segment prompt/script
"""

from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.meditations.models import Meditation, MeditationAsset, MeditationSegment
from apps.meditations.serializers import (
    MeditationAssetSerializer,
    MeditationDetailSerializer,
    MeditationListSerializer,
)
from apps.meditations.services import (
    create_meditation_for_user,
    create_pending_asset,
    set_active_asset,
)
from apps.meditations.tasks import generate_segment_part_task
from apps.users.models import User
from enums.meditation import MeditationAssetKind
from permissions import IsAdminUser
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


class AdminMeditationViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    permission_classes = [IsAdminUser]
    serializer_class = MeditationDetailSerializer

    def get_queryset(self):
        qs = Meditation.objects.select_related("user").prefetch_related(
            "segments__identity", "segments__assets"
        )
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs.order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "list":
            return MeditationListSerializer
        return MeditationDetailSerializer

    @action(detail=False, methods=["post"], url_path="create-for-user")
    def create_for_user(self, request):
        user_id = request.data.get("user_id")
        if not user_id:
            return Response(
                {"detail": "user_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = get_object_or_404(User, id=user_id)
        meditation = create_meditation_for_user(user)
        return Response(
            MeditationDetailSerializer(meditation).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="generate-part")
    def generate_part(self, request):
        segment_id = request.data.get("segment_id")
        kind = request.data.get("kind")
        if not segment_id or not kind:
            return Response(
                {"detail": "segment_id and kind are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if kind not in MeditationAssetKind.values:
            return Response(
                {"detail": f"kind must be one of {MeditationAssetKind.values}."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        segment = get_object_or_404(MeditationSegment, id=segment_id)
        # Create the QUEUED asset now so the UI sees it and starts polling
        # immediately; the task fills it in.
        asset = create_pending_asset(segment, kind)
        generate_segment_part_task.delay_on_commit(str(asset.id))
        return Response(
            MeditationAssetSerializer(asset).data,
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=False, methods=["post"], url_path="set-active")
    def set_active(self, request):
        asset_id = request.data.get("asset_id")
        if not asset_id:
            return Response(
                {"detail": "asset_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        asset = get_object_or_404(MeditationAsset, id=asset_id)
        set_active_asset(asset)
        meditation = asset.segment.meditation
        return Response(MeditationDetailSerializer(meditation).data)

    @action(detail=False, methods=["patch"], url_path="update-segment")
    def update_segment(self, request):
        segment_id = request.data.get("segment_id")
        if not segment_id:
            return Response(
                {"detail": "segment_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        segment = get_object_or_404(MeditationSegment, id=segment_id)

        update_fields = []
        if "video_prompt" in request.data:
            segment.current_video_prompt = request.data["video_prompt"]
            update_fields.append("current_video_prompt")
        if "audio_script" in request.data:
            segment.current_audio_script = request.data["audio_script"]
            update_fields.append("current_audio_script")
        if update_fields:
            update_fields.append("updated_at")
            segment.save(update_fields=update_fields)

        return Response(MeditationDetailSerializer(segment.meditation).data)
