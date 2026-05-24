"""
CoachingPhaseVideosViewSet — public endpoint exposing the Coaching Phase
Videos feature config.

Served under /api/v1/core/public/ so future public feature-flagged config
can slot in under the same namespace (e.g. core/public/<next-feature>/).
"""

import logging

from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.functions import get_coaching_phase_videos

log = logging.getLogger(__name__)


class CoachingPhaseVideosViewSet(viewsets.GenericViewSet):
    """
    ViewSet for the public Coaching Phase Videos config.

    Endpoints (trailing_slash=False router):
        GET /api/v1/core/public/coaching-phase-videos → list()
    """

    permission_classes = [AllowAny]

    def list(self, request: Request) -> Response:
        """
        GET /api/v1/core/public/coaching-phase-videos

        Return the Coaching Phase Videos config. Always returns the full
        shape; the `enabled` flag tells the frontend whether to render
        video/break components.
        """
        return Response(get_coaching_phase_videos(), status=status.HTTP_200_OK)
