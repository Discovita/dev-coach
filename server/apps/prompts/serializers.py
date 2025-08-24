from rest_framework import serializers
from .models import Prompt


class PromptSerializer(serializers.ModelSerializer):
    """
    Serializer for the Prompt model.
    """

    class Meta:
        model = Prompt
        fields = "__all__"
