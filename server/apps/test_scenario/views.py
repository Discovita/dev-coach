from rest_framework import viewsets, status, decorators, mixins, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import TestScenario
from .serializers import TestScenarioSerializer
from .validation import validate_scenario_template
from .services import instantiate_test_scenario


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
        instance = serializer.save(
            created_by=self.request.user if self.request.user.is_authenticated else None
        )
        # Instantiate scenario (user only for now)
        instantiate_test_scenario(instance, create_user=True, create_coach_state=True)

    def perform_update(self, serializer):
        template = self.request.data.get("template")
        errors = validate_scenario_template(template)
        if errors:
            raise serializers.ValidationError({"template": errors})
        instance = serializer.save()
        # Re-instantiate scenario (user only for now)
        instantiate_test_scenario(instance, create_user=True, create_coach_state=True)

    def destroy(self, request, *args, **kwargs):
        """
        Override destroy to return a success message on deletion.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Test scenario deleted successfully."}, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["post"], url_path="reset")
    def reset(self, request, pk=None):
        """
        Custom action to reset a test scenario to its original template state.
        """
        scenario = self.get_object()
        instantiate_test_scenario(scenario, create_user=True)
        instantiate_test_scenario(scenario, create_user=True, create_coach_state=True)
        return Response(
            {"success": True, "message": "Scenario reset (user only)."},
            status=status.HTTP_200_OK,
        )
