from apps.identities.models import Identity
from rest_framework import serializers
from apps.core.serializers import VersatileImageFieldWithSizes


class IdentitySerializer(serializers.ModelSerializer):
    """
    Serializer for Identity model.
    Returns image URLs for multiple sizes (original, thumbnail, medium, large).
    """

    # Force UUID to be serialized as a string (read-only, set by viewset)
    user = serializers.CharField(source="user_id", read_only=True)
    # Image field returns URLs for all sizes
    image = VersatileImageFieldWithSizes(required=False, allow_null=True, read_only=True)

    class Meta:
        model = Identity
        fields = (
            "id",
            "user",
            "name",
            "i_am_statement",
            "visualization",
            "state",
            "notes",
            "category",
            "image",
            "created_at",
            "updated_at",
        )
