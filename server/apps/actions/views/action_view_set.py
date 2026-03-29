"""
ActionViewSet — read-only HTTP API over Action rows with staff-only helpers.
"""

from django_filters import rest_framework as filters

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.actions.models import Action
from apps.actions.serializers import (
    ActionListSerializer,
    ActionSerializer,
    ByCoachMessageActionsQuerySerializer,
    ForUserActionsQuerySerializer,
)
from apps.chat_messages.models import ChatMessage


class ActionFilter(filters.FilterSet):
    """
    FilterSet for Action list (action_type, user, test_scenario).
    """

    action_type = filters.CharFilter(field_name="action_type", lookup_expr="exact")
    user = filters.UUIDFilter(field_name="user__id", lookup_expr="exact")
    test_scenario = filters.UUIDFilter(
        field_name="test_scenario__id", lookup_expr="exact"
    )

    class Meta:
        model = Action
        fields = ["action_type", "user", "test_scenario"]


class ActionViewSet(viewsets.GenericViewSet):
    """
    Authenticated read API for coach Action records.

    Endpoints (trailing_slash=False router):
    - GET /api/v1/actions              → list()
    - GET /api/v1/actions/{pk}         → retrieve()
    - GET /api/v1/actions/for-user     → for_user()
    - GET /api/v1/actions/by-coach-message → by_coach_message()
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ActionSerializer
    filterset_class = ActionFilter

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Action.objects.all().order_by("-timestamp")
        return Action.objects.filter(user=user).order_by("-timestamp")

    def get_serializer_class(self):
        if self.action == "list":
            return ActionListSerializer
        return ActionSerializer

    def list(self, request: Request) -> Response:
        """
        GET /api/v1/actions

        Paginated/filtered list of actions for the current user; staff sees all.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request: Request, pk: str | None = None) -> Response:
        """
        GET /api/v1/actions/{pk}

        Single action if visible to the current user (or staff for any row).
        """
        obj = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="for-user")
    def for_user(self, request: Request) -> Response:
        """
        GET /api/v1/actions/for-user?user_id=<uuid>

        Staff/superuser: list actions for another user. Same shape as list detail serializer.
        """
        if not request.user.is_staff and not request.user.is_superuser:
            return Response({"detail": "Not authorized."}, status=403)

        query = ForUserActionsQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        user_id = query.validated_data["user_id"]

        User = get_user_model()
        try:
            target = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)

        rows = Action.objects.filter(user=target).order_by("-timestamp")
        serializer = self.get_serializer(rows, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="by-coach-message")
    def by_coach_message(self, request: Request) -> Response:
        """
        GET /api/v1/actions/by-coach-message?message_id=<uuid>

        Actions for one coach message; non-staff only if the message belongs to them.
        """
        query = ByCoachMessageActionsQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        message_id = query.validated_data["message_id"]

        message = get_object_or_404(ChatMessage, pk=message_id)
        if not request.user.is_staff and message.user_id != request.user.id:
            return Response({"detail": "Not authorized."}, status=403)

        rows = Action.objects.filter(coach_message=message).order_by("timestamp")
        serializer = self.get_serializer(rows, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
