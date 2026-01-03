"""
ViewSet for Reference Images CRUD operations.
Thin view layer - delegates all business logic to functions.
"""

from rest_framework import viewsets, status, decorators
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from services.logger import configure_logging

from apps.reference_images.models import ReferenceImage
from apps.reference_images.serializers import ReferenceImageSerializer
from apps.reference_images.functions.public import (
    create_reference_image,
    upload_reference_image,
    delete_reference_image,
)
from apps.reference_images.functions.admin import create_reference_image_for_user

log = configure_logging(__name__, log_level="INFO")


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
        log.info(f"Getting reference images queryset. user_id param: {user_id}, is_staff: {self.request.user.is_staff}")
        
        try:
            if user_id and self.request.user.is_staff:
                log.info(f"Admin query: filtering by user_id={user_id}")
                queryset = ReferenceImage.objects.filter(user_id=user_id)
                count = queryset.count()
                log.info(f"Found {count} reference images for user {user_id}")
                return queryset
            else:
                log.info(f"User query: filtering by current user={self.request.user.id}")
                queryset = ReferenceImage.objects.filter(user=self.request.user)
                count = queryset.count()
                log.info(f"Found {count} reference images for current user")
                return queryset
        except Exception as e:
            log.error(f"Error in get_queryset: {e}", exc_info=True)
            raise

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Create a new reference image."""
        log.info(f"Creating reference image. user_id: {request.data.get('user_id')}, order: {request.data.get('order')}, has_image: {bool(request.FILES.get('image'))}")
        
        try:
            user_id = request.data.get("user_id")
            
            # Convert order to int if provided (FormData sends strings)
            order_raw = request.data.get("order")
            order = None
            if order_raw is not None:
                try:
                    order = int(order_raw)
                    log.debug(f"Converted order from {order_raw} to {order}")
                except (ValueError, TypeError) as e:
                    log.warning(f"Invalid order value: {order_raw}, error: {e}")
                    return Response(
                        {"error": "Order must be a valid integer"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Admin creating for another user
            if user_id and request.user.is_staff:
                log.info(f"Admin creating reference image for user {user_id}")
                ref_image = create_reference_image_for_user(
                    user_id=user_id,
                    name=request.data.get("name", ""),
                    order=order,
                    image_file=request.FILES.get("image"),
                )
                log.info(f"Successfully created reference image {ref_image.id} for user {user_id}")
            else:
                # User creating for themselves
                log.info(f"User creating reference image for themselves")
                ref_image = create_reference_image(
                    user=request.user,
                    name=request.data.get("name", ""),
                    order=order,
                    image_file=request.FILES.get("image"),
                )
                log.info(f"Successfully created reference image {ref_image.id} for user {request.user.id}")

            log.info(f"Serializing reference image {ref_image.id}")
            serializer_data = ReferenceImageSerializer(ref_image).data
            log.info(f"Successfully serialized reference image {ref_image.id}")
            
            return Response(serializer_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            log.error(f"Error creating reference image: {e}", exc_info=True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request: Request, *args, **kwargs) -> Response:
        """List reference images."""
        log.info(f"Listing reference images for request")
        try:
            queryset = self.get_queryset()
            log.info(f"Queryset retrieved, serializing {queryset.count()} images")
            
            serializer = ReferenceImageSerializer(queryset, many=True)
            log.info(f"Serialization complete, returning {len(serializer.data)} images")
            
            return Response(serializer.data)
        except Exception as e:
            log.error(f"Error listing reference images: {e}", exc_info=True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """Delete a reference image."""
        log.info(f"Deleting reference image")
        try:
            ref_image = self.get_object()
            log.info(f"Found reference image {ref_image.id}, deleting")
            delete_reference_image(ref_image)
            log.info(f"Successfully deleted reference image {ref_image.id}")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            log.error(f"Error deleting reference image: {e}", exc_info=True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @decorators.action(detail=True, methods=["POST"], url_path="upload-image")
    def upload_image(self, request: Request, pk=None) -> Response:
        """Upload or replace the image file for a reference image."""
        log.info(f"Uploading image for reference image {pk}")
        try:
            ref_image = self.get_object()
            log.info(f"Found reference image {ref_image.id} for user {ref_image.user_id}")

            updated = upload_reference_image(
                reference_image=ref_image,
                image_file=request.FILES.get("image"),
            )
            log.info(f"Successfully uploaded image for reference image {updated.id}")

            serializer_data = ReferenceImageSerializer(updated).data
            log.info(f"Successfully serialized updated reference image {updated.id}")
            
            return Response(serializer_data)
        except Exception as e:
            log.error(f"Error uploading image: {e}", exc_info=True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

