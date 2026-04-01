from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.coach.functions.public import process_message
from apps.coach.serializers import AdminCoachRequestSerializer, CoachResponseSerializer
from permissions import IsAdminUser
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")

User = get_user_model()


class AdminCoachViewSet(viewsets.GenericViewSet):
    """
    Admin ViewSet for coach message processing.

    Endpoints:
    - POST /api/v1/admin/coach/process-message-for-user/  → process_message_for_user()
    """

    @action(
        detail=False,
        methods=["post"],
        url_path="process-message-for-user",
        permission_classes=[IsAdminUser],
    )
    def process_message_for_user(self, request: Request) -> Response:
        """
        POST /api/v1/admin/coach/process-message-for-user/

        Process a message as if sent by a specific user (admin only).

        Request Body:
            {
                "user_id": str,
                "message": str,
                "actions": list (optional)
            }

        Response:
            200: { "message": str, "final_prompt": str, "component": dict (optional) }
            404: { "detail": str } - User not found
            500: { "detail": str } - Processing error
        """
        serializer = AdminCoachRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data["user_id"]
        message = serializer.validated_data["message"]
        model = serializer.get_model()
        actions = serializer.validated_data.get("actions", [])

        try:
            acting_user = User.objects.get(pk=user_id)
            log.debug(f"Admin {request.user} processing message for user {acting_user}")
        except User.DoesNotExist:
            log.error(f"User with id {user_id} not found")
            return Response(
                {"detail": f"User with id {user_id} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        success, response_data, error_message = process_message(
            user=acting_user,
            message=message,
            request_component_actions=actions,
            model=model,
        )

        if not success:
            log.error(f"Error processing message for user {acting_user.id}: {error_message}")
            return Response(
                {"detail": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        response_serializer = CoachResponseSerializer(data=response_data)
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
