"""
Model serializer for UserNote.

See: apps/user_notes/serializers/__init__.py
"""

from rest_framework import serializers

from apps.user_notes.models import UserNote


class UserNoteSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserNote model.

    Used for API serialization and scenario template validation.
    """

    class Meta:
        model = UserNote
        fields = [
            "id",
            "user",
            "note",
            "source_message",
            "created_at",
            "test_scenario",
        ]
        read_only_fields = ["id", "created_at"]
