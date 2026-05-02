"""
Admin-only viewset for managing Prompt records.

See: apps/prompts/views/__init__.py
"""

from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.prompts.models import Prompt
from apps.prompts.serializers import PromptSerializer
from apps.prompts.utils import get_next_prompt_version
from enums.coaching_phase import CoachingPhase
from enums.prompt_type import PromptType
from permissions import IsAdminUser


class PromptViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Admin-only CRUD endpoints for managing prompts.

    Supported operations:
    - list:           GET    /api/prompts/                 Active prompts
    - retrieve:       GET    /api/prompts/{id}/            Single prompt
    - create:         POST   /api/prompts/                 Create (version auto-assigned)
    - update:         PUT    /api/prompts/{id}/            Full update
    - partial_update: PATCH  /api/prompts/{id}/            Partial update
    - destroy:        DELETE /api/prompts/{id}/            Hard delete
    - soft_delete:    POST   /api/prompts/{id}/soft_delete Set is_active=False
    - latest:         GET    /api/prompts/latest?coaching_phase=...
    """

    permission_classes = [IsAdminUser]
    serializer_class = PromptSerializer

    def get_queryset(self):
        """Return active prompts for list, all prompts otherwise."""
        if self.action == "list":
            return Prompt.objects.filter(is_active=True)
        return Prompt.objects.all()

    def create(self, request, *args, **kwargs):
        """
        Create a new prompt with auto-assigned version.

        Version is determined by the latest existing version for the same
        (prompt_type, coaching_phase) combination. Any version value sent
        by the client is ignored.
        """
        data = request.data.copy()
        coaching_phase = data.get("coaching_phase")
        prompt_type = data.get("prompt_type", PromptType.COACH)
        data["version"] = get_next_prompt_version(prompt_type, coaching_phase)

        serializer = PromptSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="soft_delete")
    def soft_delete(self, request, pk=None):
        """Set is_active=False instead of deleting the record."""
        instance = get_object_or_404(Prompt, pk=pk)
        instance.is_active = False
        instance.save(update_fields=["is_active", "updated_at"])
        serializer = PromptSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="latest")
    def latest(self, request):
        """
        Return the latest active prompt for a given coaching phase.

        Query params:
            coaching_phase (required): A valid CoachingPhase value.
        """
        coaching_phase = request.query_params.get("coaching_phase")
        if not coaching_phase:
            return Response(
                {"detail": "coaching_phase query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            CoachingPhase.from_string(coaching_phase)
        except ValueError:
            valid_phases = [phase.value for phase in CoachingPhase]
            return Response(
                {
                    "detail": (
                        f"Invalid coaching_phase: {coaching_phase}. "
                        f"Valid phases: {valid_phases}"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        latest_prompt = (
            Prompt.objects.filter(coaching_phase=coaching_phase, is_active=True)
            .order_by("-version")
            .first()
        )

        if not latest_prompt:
            return Response(
                {
                    "detail": (
                        f"No active prompt found for coaching phase: {coaching_phase}"
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PromptSerializer(latest_prompt)
        return Response(serializer.data, status=status.HTTP_200_OK)
