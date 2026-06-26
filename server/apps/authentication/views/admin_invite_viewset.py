"""
AdminInviteViewSet — super-admin-only management of invites.

Endpoints (all gated by ``IsSuperUser``):
- GET    /api/v1/admin/invites          — list invites (newest first)
- POST   /api/v1/admin/invites          — create + email an invite {email}
- POST   /api/v1/admin/invites/{id}/resend — re-send (refreshes expiry)
- DELETE /api/v1/admin/invites/{id}     — revoke a pending invite
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.authentication.models import Invite
from apps.authentication.serializers.invite_serializer import (
    CreateInviteSerializer,
    InviteSerializer,
)
from apps.authentication.utils.send_invite_email import send_invite_email
from apps.users.models import User
from permissions import IsSuperUser
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


class AdminInviteViewSet(viewsets.GenericViewSet):
    """Super-admin CRUD for email-bound invites."""

    permission_classes = [IsSuperUser]
    queryset = Invite.objects.all()
    serializer_class = InviteSerializer

    def list(self, request: Request) -> Response:
        """GET /api/v1/admin/invites — all invites, newest first."""
        invites = Invite.objects.select_related("invited_by").all()
        return Response(InviteSerializer(invites, many=True).data)

    def create(self, request: Request) -> Response:
        """POST /api/v1/admin/invites — create + email an invite."""
        serializer = CreateInviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        if User.objects.filter(email__iexact=email).exists():
            return Response(
                {"error": "A user with that email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Reuse a still-pending invite for the same address instead of
        # stacking duplicates; refresh its expiry on re-send.
        invite = (
            Invite.objects.filter(email__iexact=email, accepted_at__isnull=True)
            .order_by("-created_at")
            .first()
        )
        if invite and invite.is_pending:
            invite.refresh_expiry()
            invite.save(update_fields=["expires_at", "updated_at"])
        else:
            invite = Invite.objects.create(email=email, invited_by=request.user)

        email_sent = send_invite_email(invite)
        data = InviteSerializer(invite).data
        return Response(
            {**data, "email_sent": email_sent}, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["post"])
    def resend(self, request: Request, pk=None) -> Response:
        """POST /api/v1/admin/invites/{id}/resend — refresh expiry + re-email."""
        try:
            invite = Invite.objects.get(pk=pk)
        except Invite.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if invite.is_accepted:
            return Response(
                {"error": "This invite has already been accepted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invite.refresh_expiry()
        invite.save(update_fields=["expires_at", "updated_at"])
        email_sent = send_invite_email(invite)
        data = InviteSerializer(invite).data
        return Response({**data, "email_sent": email_sent})

    def destroy(self, request: Request, pk=None) -> Response:
        """DELETE /api/v1/admin/invites/{id} — revoke an invite."""
        try:
            invite = Invite.objects.get(pk=pk)
        except Invite.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        invite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
