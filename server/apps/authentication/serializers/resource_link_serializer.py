"""
Serializer for the resourceLink object in LTI launch requests.
"""

from rest_framework import serializers


class ResourceLinkSerializer(serializers.Serializer):
    """Validates the ``resourceLink`` payload in an LTI launch request."""

    id = serializers.CharField(help_text="LTI resource link identifier.")
