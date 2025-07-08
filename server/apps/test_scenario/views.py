from rest_framework import viewsets, status, decorators, mixins, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import TestScenario
from .serializers import TestScenarioSerializer
from .validation import validate_scenario_template


class TestScenarioViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet for managing test scenarios.
    Endpoints:
    - list, retrieve, create, update, delete
    - reset (custom action)
    """

    queryset = TestScenario.objects.all()
    serializer_class = TestScenarioSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        template = self.request.data.get("template")
        errors = validate_scenario_template(template)
        if errors:
            raise serializers.ValidationError({"template": errors})
        serializer.save(
            created_by=self.request.user if self.request.user.is_authenticated else None
        )

    def perform_update(self, serializer):
        template = self.request.data.get("template")
        errors = validate_scenario_template(template)
        if errors:
            raise serializers.ValidationError({"template": errors})
        serializer.save()

    @decorators.action(detail=True, methods=["post"], url_path="reset")
    def reset(self, request, pk=None):
        """
        Custom action to reset a test scenario to its original template state.
        (Implementation to be added)
        """
        # TODO: Implement scenario reset logic
        return Response(
            {"success": True, "message": "Reset not yet implemented."},
            status=status.HTTP_200_OK,
        )
