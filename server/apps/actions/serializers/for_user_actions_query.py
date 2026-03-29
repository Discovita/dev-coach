"""
Query parameter validation for GET .../actions/for-user.
"""

from rest_framework import serializers


class ForUserActionsQuerySerializer(serializers.Serializer):
    """
    Validates query params for listing another user's actions (staff/superuser).
    """

    user_id = serializers.UUIDField(
        help_text="Target user primary key (UUID).",
    )
