from apps.identities.models import Identity
from rest_framework import serializers


class IdentitySerializer(serializers.ModelSerializer):
    """
    Serializer for Identity model.
    Used to serialize user identities when included in UserSerializer.
    """

    # Force UUID to be serialized as a string
    user = serializers.CharField(source="user_id")

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
            "created_at",
            "updated_at",
        )
