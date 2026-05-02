"""
ViewSet for Reference Image CRUD and image upload.

See: apps/reference_images/views/__init__.py
"""

from django.shortcuts import get_object_or_404
from rest_framework import decorators, mixins, status, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.reference_images.functions.admin import create_reference_image_for_user
from apps.reference_images.functions.public import (
    create_reference_image,
    delete_reference_image,
    upload_reference_image,
)
from apps.reference_images.models import ReferenceImage
from apps.reference_images.serializers import ReferenceImageSerializer


class ReferenceImageViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    CRUD and image upload for reference images.

    Regular users can only manage their own images. Admin users can manage
    images for any user via the ``user_id`` parameter.

    Endpoints:
    - GET    /api/v1/reference-images/                      List (own or ?user_id=)
    - POST   /api/v1/reference-images/                      Create
    - GET    /api/v1/reference-images/{id}/                  Retrieve
    - PATCH  /api/v1/reference-images/{id}/                  Update
    - DELETE /api/v1/reference-images/{id}/                  Delete
    - POST   /api/v1/reference-images/{id}/upload-image/     Upload/replace image
    """

    serializer_class = ReferenceImageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        """
        Scope queryset based on user role and action.

        - Admin detail actions (retrieve, update, destroy, upload_image):
          return all images so the admin can operate on any user's image.
        - Admin list with ``user_id`` param: filter to that user.
        - Otherwise: current user's images only.
        """
        detail_actions = {
            "retrieve",
            "update",
            "partial_update",
            "destroy",
            "upload_image",
        }

        if self.request.user.is_staff and self.action in detail_actions:
            return ReferenceImage.objects.all()

        user_id = self.request.query_params.get("user_id")
        if user_id and self.request.user.is_staff:
            return ReferenceImage.objects.filter(user_id=user_id)

        return ReferenceImage.objects.filter(user=self.request.user)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Create a new reference image.

        Admins may pass ``user_id`` in the request body to create an image
        for another user. Regular users always create for themselves.
        """
        user_id = request.data.get("user_id")

        order_raw = request.data.get("order")
        order = None
        if order_raw is not None:
            try:
                order = int(order_raw)
            except (ValueError, TypeError):
                return Response(
                    {"detail": "Order must be a valid integer."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if user_id and request.user.is_staff:
            ref_image = create_reference_image_for_user(
                user_id=user_id,
                name=request.data.get("name", ""),
                order=order,
                image_file=request.FILES.get("image"),
            )
        else:
            ref_image = create_reference_image(
                user=request.user,
                name=request.data.get("name", ""),
                order=order,
                image_file=request.FILES.get("image"),
            )

        return Response(
            ReferenceImageSerializer(ref_image).data,
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """Delete a reference image and its associated file."""
        instance = get_object_or_404(self.get_queryset(), pk=kwargs["pk"])
        delete_reference_image(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(detail=True, methods=["POST"], url_path="upload-image")
    def upload_image(self, request: Request, pk=None) -> Response:
        """Upload or replace the image file for a reference image."""
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        updated = upload_reference_image(
            reference_image=instance,
            image_file=request.FILES.get("image"),
        )
        return Response(ReferenceImageSerializer(updated).data)
