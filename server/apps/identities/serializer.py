from apps.identities.models import Identity
from rest_framework import serializers


class IdentitySerializer(serializers.ModelSerializer):
    """
    Serializer for Identity model.
    Used to serialize user identities when included in UserSerializer.
    """

    class Meta:
        model = Identity
        fields = (
            "id",
            "user",
            "name",
            "affirmation",
            "visualization",
            "state",
            "notes",
            "category",
            "created_at",
            "updated_at",
        )
