from rest_framework import serializers
from apps.coach_states.models import CoachState


class CoachStateSerializer(serializers.ModelSerializer):
    # Force UUID to be serialized as a string
    user = serializers.CharField(source="user_id")

    class Meta:
        model = CoachState
        fields = "__all__"  # or list the fields you want
