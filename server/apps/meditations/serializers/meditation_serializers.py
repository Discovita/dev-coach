"""
Serializers for the meditations admin API.
"""

from django.core.files.storage import default_storage
from rest_framework import serializers

from apps.meditations.models import Meditation, MeditationAsset, MeditationSegment


class MeditationAssetSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = MeditationAsset
        fields = (
            "id",
            "kind",
            "version",
            "status",
            "is_active",
            "s3_key",
            "url",
            "prompt_snapshot",
            "error_code",
            "created_at",
            "updated_at",
        )

    def get_url(self, obj):
        if not obj.s3_key:
            return None
        return default_storage.url(obj.s3_key)


class MeditationSegmentSerializer(serializers.ModelSerializer):
    assets = MeditationAssetSerializer(many=True, read_only=True)
    identity_name = serializers.CharField(source="identity.name", read_only=True)

    class Meta:
        model = MeditationSegment
        fields = (
            "id",
            "identity",
            "identity_name",
            "order",
            "current_video_prompt",
            "current_audio_script",
            "assets",
        )


class MeditationDetailSerializer(serializers.ModelSerializer):
    segments = MeditationSegmentSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Meditation
        fields = (
            "id",
            "user",
            "user_email",
            "status",
            "final_video_s3_key",
            "segments",
            "created_at",
            "updated_at",
        )


class MeditationListSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    segment_count = serializers.IntegerField(source="segments.count", read_only=True)

    class Meta:
        model = Meditation
        fields = (
            "id",
            "user",
            "user_email",
            "status",
            "segment_count",
            "created_at",
            "updated_at",
        )
