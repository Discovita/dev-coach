from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.request import Request
from apps.coach.serializers import CoachRequestSerializer, CoachResponseSerializer
from apps.coach.services.coach_service import CoachService
from rest_framework.decorators import action
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


class CoachViewSet(viewsets.GenericViewSet):
    """Endpoints for processing coach messages for authenticated users."""

    @action(
        detail=False,
        methods=["post"],
        url_path="process-message",
        permission_classes=[IsAuthenticated],
    )
    def process_message(self, request: Request):
        """Process a message for the authenticated user."""
        serializer = CoachRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = serializer.validated_data["message"]
        actions = serializer.validated_data.get("actions", [])
        model = serializer.get_model()

        success, response_data, error_message = CoachService.process_message(
            user=request.user,
            message=message,
            request_component_actions=actions,
            model=model,
        )

        if not success:
            log.error(f"Error processing message: {error_message}")
            return Response(
                {"detail": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        response_serializer = CoachResponseSerializer(data=response_data)
        response_serializer.is_valid(raise_exception=True)

        return Response(response_serializer.data, status=status.HTTP_200_OK)
