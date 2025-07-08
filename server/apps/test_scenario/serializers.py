from rest_framework import serializers
from .models import TestScenario

class TestScenarioSerializer(serializers.ModelSerializer):
    """
    Serializer for the TestScenario model.
    Used for CRUD operations in the TestScenarioViewSet.
    """
    class Meta:
        model = TestScenario
        fields = '__all__' 