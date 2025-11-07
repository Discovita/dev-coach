from apps.identities.models import Identity
from rest_framework import serializers


class IdentitySerializer(serializers.ModelSerializer):
    """
    Serializer for Identity model.
    Used to serialize user identities when included in UserSerializer.
    Handles image uploads via ImageField, which automatically uses S3 in production/staging
    and local storage in development.
    """

    # Force UUID to be serialized as a string (read-only, set by viewset)
    user = serializers.CharField(source="user_id", read_only=True)
    # Image field will automatically return full URL (S3 URL in prod/staging, local URL in dev)
    image = serializers.ImageField(required=False, allow_null=True)

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
