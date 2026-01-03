from rest_framework import serializers
from apps.reference_images.models import ReferenceImage
from apps.core.serializers import VersatileImageFieldWithSizes


class ReferenceImageSerializer(serializers.ModelSerializer):
    """Serializer for ReferenceImage model."""

    user = serializers.CharField(source="user_id", read_only=True)
    image = VersatileImageFieldWithSizes(required=False, allow_null=True, read_only=True)

    class Meta:
        model = ReferenceImage
        fields = ("id", "user", "name", "order", "image", "created_at", "updated_at")
        read_only_fields = ("id", "user", "created_at", "updated_at")

