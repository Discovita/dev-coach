"""
CoachStateSerializer

Serializes CoachState for API responses.

Handles local database fields and includes nested identity data for the current
identity being refined.
"""

from rest_framework import serializers

from apps.coach_states.models import CoachState
from apps.identities.serializer import IdentitySerializer


class CoachStateSerializer(serializers.ModelSerializer):
    """
    Serializes CoachState for API responses.

    Includes nested identity data for the current identity being refined.
    """

    # Force UUID to be serialized as a string
    user = serializers.CharField(
        source="user_id",
        help_text="User ID this coach state belongs to (UUID as string).",
    )

    # Include nested identity data for current and proposed identities
    current_identity = IdentitySerializer(
        read_only=True,
        help_text="The Identity currently being refined (nested data).",
    )
    proposed_identity = IdentitySerializer(
        read_only=True,
        help_text="The currently proposed identity (nested data).",
    )

    class Meta:
        model = CoachState
        fields = (
            "id",  # Unique identifier for the coach state
            "user",  # User ID this coach state belongs to
            "current_phase",  # Current phase of the coaching session
            "current_identity",  # The identity currently being refined
            "proposed_identity",  # The currently proposed identity
            "identity_focus",  # The current category focus
            "skipped_identity_categories",  # List of skipped identity categories
            "who_you_are",  # List of 'who you are' identities
            "who_you_want_to_be",  # List of 'who you want to be' identities
            "asked_questions",  # List of questions asked during Get To Know You phase
            "updated_at",  # Timestamp of last update
        )
        read_only_fields = (
            "id",
            "user",
            "current_identity",
            "proposed_identity",
            "updated_at",
        )
