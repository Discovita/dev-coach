from rest_framework import serializers
from .models import UserNote

class UserNoteSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserNote model.
    Used for API serialization and scenario template validation.
    """
    class Meta:
        model = UserNote
        fields = '__all__' 