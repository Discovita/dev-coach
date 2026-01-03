"""
ViewSet for Reference Images CRUD operations.
Thin view layer - delegates all business logic to functions.
"""

from rest_framework import viewsets, status, decorators
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import logging

from apps.reference_images.models import ReferenceImage
from apps.reference_images.serializers import ReferenceImageSerializer
from apps.reference_images.functions.public import (
    create_reference_image,
    upload_reference_image,
    delete_reference_image,
)
from apps.reference_images.functions.admin import create_reference_image_for_user

log = logging.getLogger(__name__)


class ReferenceImageViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for reference images.
    Admin users can manage reference images for any user.
    Regular users can only manage their own reference images.

    Endpoints:
    - GET /api/v1/reference-images/?user_id={uuid} - List reference images for a user
    - POST /api/v1/reference-images/ - Create new reference image
    - GET /api/v1/reference-images/{id}/ - Get single reference image
    - PATCH /api/v1/reference-images/{id}/ - Update reference image
    - DELETE /api/v1/reference-images/{id}/ - Delete reference image
    - POST /api/v1/reference-images/{id}/upload-image/ - Upload/replace image file
    """

    serializer_class = ReferenceImageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        """Filter by user_id query param or default to current user."""
        user_id = self.request.query_params.get("user_id")
        if user_id and self.request.user.is_staff:
            return ReferenceImage.objects.filter(user_id=user_id)
        return ReferenceImage.objects.filter(user=self.request.user)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Create a new reference image."""
        user_id = request.data.get("user_id")

        # Admin creating for another user
        if user_id and request.user.is_staff:
            ref_image = create_reference_image_for_user(
                user_id=user_id,
                name=request.data.get("name", ""),
                order=request.data.get("order"),
                image_file=request.FILES.get("image"),
            )
        else:
            # User creating for themselves
            ref_image = create_reference_image(
                user=request.user,
                name=request.data.get("name", ""),
                order=request.data.get("order"),
                image_file=request.FILES.get("image"),
            )

        return Response(
            ReferenceImageSerializer(ref_image).data, status=status.HTTP_201_CREATED
        )

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """Delete a reference image."""
        ref_image = self.get_object()
        delete_reference_image(ref_image)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(detail=True, methods=["POST"], url_path="upload-image")
    def upload_image(self, request: Request, pk=None) -> Response:
        """Upload or replace the image file for a reference image."""
        ref_image = self.get_object()

        updated = upload_reference_image(
            reference_image=ref_image,
            image_file=request.FILES.get("image"),
        )

        return Response(ReferenceImageSerializer(updated).data)

