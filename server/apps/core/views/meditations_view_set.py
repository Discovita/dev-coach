"""
MeditationsViewSet — public endpoint exposing the Meditations feature config.

Served under /api/v1/core/public/ alongside the other public feature-flag
config endpoints.
"""

import logging

from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.functions import get_meditations

log = logging.getLogger(__name__)


class MeditationsViewSet(viewsets.GenericViewSet):
    """
    ViewSet for the public Meditations config.

    Endpoints (trailing_slash=False router):
        GET /api/v1/core/public/meditations → list()
    """

    permission_classes = [AllowAny]

    def list(self, request: Request) -> Response:
        """
        GET /api/v1/core/public/meditations

        Return the Meditations config. Always returns the full shape; the
        `enabled` flag tells the frontend whether to show the meditations
        surface.
        """
        return Response(get_meditations(), status=status.HTTP_200_OK)
