"""
AdminTestScenarioViewSet — admin-only ViewSet for test scenario management.

Thin view layer — business logic lives in ``functions/`` and ``utils/``.

See: apps/test_scenario/views/__init__.py
"""

import json

from rest_framework import decorators, mixins, serializers, status, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from apps.test_scenario.functions import (
    FreezeSessionError,
    freeze_user_session,
    instantiate_test_scenario,
)
from apps.test_scenario.models import TestScenario
from apps.test_scenario.serializers import TestScenarioSerializer
from apps.test_scenario.utils.process_identity_images import process_identity_images
from apps.test_scenario.utils.validate_scenario_template import (
    validate_scenario_template,
)
from permissions import IsAdminUser


class AdminTestScenarioViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    Admin-only CRUD for test scenarios.

    Custom actions:
        - ``POST /<pk>/reset/`` — re-instantiate a scenario from its template.
        - ``POST /freeze-session/`` — capture a live user session as a new scenario.
    """

    queryset = TestScenario.objects.all()
    serializer_class = TestScenarioSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    # ------------------------------------------------------------------
    # Create / Update hooks
    # ------------------------------------------------------------------

    def perform_create(self, serializer) -> None:
        template = _parse_template(self.request)
        template = process_identity_images(self.request, template)
        _validate_or_raise(template)

        serializer.validated_data["template"] = template
        instance = serializer.save(
            created_by=self.request.user if self.request.user.is_authenticated else None
        )
        _instantiate_all(instance)

    def perform_update(self, serializer) -> None:
        instance = self.get_object()
        old_template = instance.template

        template = _parse_template(self.request)
        template = process_identity_images(
            self.request, template, old_template=old_template
        )
        _validate_or_raise(template)

        serializer.validated_data["template"] = template
        instance = serializer.save()
        _instantiate_all(instance)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"success": True, "message": "Test scenario deleted successfully."},
            status=status.HTTP_200_OK,
        )

    # ------------------------------------------------------------------
    # Custom actions
    # ------------------------------------------------------------------

    @decorators.action(detail=True, methods=["post"], url_path="reset")
    def reset(self, request, pk=None):
        """Re-instantiate a scenario from its stored template."""
        scenario = self.get_object()
        _instantiate_all(scenario)
        return Response(
            {"success": True, "message": "Scenario reset (all data)."},
            status=status.HTTP_200_OK,
        )

    @decorators.action(detail=False, methods=["post"], url_path="freeze-session")
    def freeze_session(self, request):
        """Capture a live user session as a new test scenario."""
        try:
            scenario = freeze_user_session(
                user_id=request.data.get("user_id"),
                name=request.data.get("name"),
                description=request.data.get("description", ""),
                first_name=request.data.get("first_name", ""),
                last_name=request.data.get("last_name", ""),
                created_by=(request.user if request.user.is_authenticated else None),
            )
        except FreezeSessionError as exc:
            return Response(
                {"detail": exc.detail},
                status=exc.status_code,
            )

        return Response(
            TestScenarioSerializer(scenario).data,
            status=status.HTTP_201_CREATED,
        )


# ----------------------------------------------------------------------
# Module-private helpers
# ----------------------------------------------------------------------


def _parse_template(request) -> dict:
    """Extract the template from a request, handling JSON-string payloads."""
    template_data = request.data.get("template")
    if not template_data:
        raise serializers.ValidationError({"template": "Template is required"})

    if isinstance(template_data, str):
        try:
            return json.loads(template_data)
        except json.JSONDecodeError as e:
            raise serializers.ValidationError(
                {"template": f"Invalid JSON in template: {e}"}
            )
    return template_data


def _validate_or_raise(template: dict) -> None:
    """Run template validation and raise on errors."""
    errors = validate_scenario_template(template)
    if errors:
        raise serializers.ValidationError({"template": errors})


def _instantiate_all(scenario) -> None:
    """Instantiate every section of a scenario."""
    instantiate_test_scenario(
        scenario,
        create_user=True,
        create_coach_state=True,
        create_identities=True,
        create_chat_messages=True,
        create_user_notes=True,
        create_actions=True,
    )
