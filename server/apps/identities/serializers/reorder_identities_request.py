"""
Serializer for the identity reorder endpoint.

Validates the incoming ordered list of identity IDs and ensures every ID
belongs to the requesting user. The viewset stays a thin coordinator;
ownership/validation lives here.
"""

from rest_framework import serializers

from apps.identities.models import Identity


class ReorderIdentitiesRequestSerializer(serializers.Serializer):
    """
    Request body: ``{"ordered_ids": [uuid, uuid, ...]}``.

    The list defines the new ascending display order — index 0 is shown first.
    Requires the ``user`` in serializer context for ownership validation.
    """

    ordered_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
        help_text="Identity IDs in the desired display order (first = top).",
    )

    def validate_ordered_ids(self, value):
        """Ensure no duplicates and every ID belongs to the requesting user."""
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate identity IDs are not allowed.")

        user = self.context["user"]
        owned_ids = set(
            Identity.objects.filter(user=user, id__in=value).values_list(
                "id", flat=True
            )
        )
        unknown = [str(i) for i in value if i not in owned_ids]
        if unknown:
            raise serializers.ValidationError(
                f"These identities do not belong to the user: {', '.join(unknown)}"
            )
        return value
