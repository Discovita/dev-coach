"""
Serializer for the Prompt model.

See: apps/prompts/serializers/__init__.py
"""

from rest_framework import serializers

from apps.prompts.models import Prompt


class PromptSerializer(serializers.ModelSerializer):
    """
    Serializer for the Prompt model.

    Provides read/write access to all prompt fields. Version is
    writable here but auto-assigned by the create view — any client
    value is overridden at that layer.
    """

    class Meta:
        model = Prompt
        fields = [
            "id",
            "coaching_phase",
            "version",
            "name",
            "description",
            "body",
            "required_context_keys",
            "allowed_actions",
            "prompt_type",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
