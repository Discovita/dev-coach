from rest_framework import serializers

from apps.coach.serializers.coach_request_serializer import CoachRequestSerializer


class AdminCoachRequestSerializer(CoachRequestSerializer):
    """
    Serializer for incoming admin request to the coach endpoint.

    Extends CoachRequestSerializer with a required user_id field,
    allowing admins to process messages on behalf of any user.
    """

    user_id = serializers.UUIDField(
        required=True,
        help_text="User ID to act as (admin only).",
    )
