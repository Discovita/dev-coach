from rest_framework import serializers
from .models import TestScenario
from django.utils.translation import gettext_lazy as _
from apps.users.models import User

class TestScenarioSerializer(serializers.ModelSerializer):
    """
    Serializer for the TestScenario model.
    Used for CRUD operations in the TestScenarioViewSet.
    """
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = TestScenario
        fields = '__all__'

    def get_created_by(self, obj):
        user = obj.created_by
        if not user:
            return None
        full_name = user.get_full_name()
        if full_name:
            return full_name
        return user.email 