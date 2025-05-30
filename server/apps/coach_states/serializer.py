from rest_framework import serializers
from apps.coach_states.models import CoachState
from apps.identities.serializer import IdentitySerializer


class CoachStateSerializer(serializers.ModelSerializer):
    # Force UUID to be serialized as a string
    user = serializers.CharField(source="user_id")
    # Include nested identity data for current and proposed identities
    current_identity = IdentitySerializer(read_only=True)
    proposed_identity = IdentitySerializer(read_only=True)

    class Meta:
        model = CoachState
        fields = (
            "id",  # Unique identifier for the coach state
            "user",  # User ID this coach state belongs to
            "current_phase",  # Current phase of the coaching session
            "current_identity",  # The identity currently being refined
            "proposed_identity",  # The currently proposed identity
            "metadata",  # Additional metadata for the coaching session
            "updated_at",  # Timestamp of last update
        )
        read_only_fields = (
            "id",
            "user",
            "current_identity",
            "proposed_identity",
            "updated_at",
        )
