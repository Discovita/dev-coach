from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from django.shortcuts import get_object_or_404
from django.http import Http404
from .models import Identity
from .serializer import IdentitySerializer
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


class IdentityViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    API endpoint for managing user identities.

    Supported operations:
    - list:    GET    /api/v1/identities/         List all identities for authenticated user
    - retrieve:GET    /api/v1/identities/{id}/    Retrieve a single identity by ID
    - create:  POST   /api/v1/identities/         Create a new identity
    - update:  PUT    /api/v1/identities/{id}/    Update an identity (full update)
    - partial_update:PATCH /api/v1/identities/{id}/ Partial update of an identity
    - destroy: DELETE /api/v1/identities/{id}/    Delete an identity
    - upload_image: PATCH/PUT /api/v1/identities/{id}/upload-image/ Upload or update image
    - delete_image: DELETE /api/v1/identities/{id}/delete-image/ Delete image

    All operations are scoped to the authenticated user's identities only.
    """

    serializer_class = IdentitySerializer
    permission_classes = [IsAuthenticated]
    # Support both JSON and multipart/form-data for image uploads
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        """
        Return only identities belonging to the authenticated user.
        """
        return Identity.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        List all identities for the authenticated user.
        GET /api/v1/identities/
        Returns: 200 OK, list of user's identities.
        """
        try:
            identities = Identity.objects.filter(user=request.user)
            serializer = IdentitySerializer(identities, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            log.error(f"Error listing identities: {str(e)}", exc_info=True)
            return Response(
                {"success": False, "error": "Server error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single identity by ID.
        GET /api/v1/identities/{id}/
        Returns: 200 OK, identity object.
        """
        try:
            pk = kwargs.get("pk")
            identity = get_object_or_404(Identity, id=pk, user=request.user)
            serializer = IdentitySerializer(identity)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404:
            return Response(
                {"success": False, "error": "Identity not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            log.error(f"Error retrieving identity: {str(e)}", exc_info=True)
            return Response(
                {"success": False, "error": "Server error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def create(self, request, *args, **kwargs):
        """
        Create a new identity for the authenticated user.
        POST /api/v1/identities/
        Body: Identity fields (see IdentitySerializer)
        Returns: 201 Created, created identity object.
        """
        try:
            serializer = IdentitySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            # Ensure the identity is created for the authenticated user
            identity = serializer.save(user=request.user)
            log.info(f"Created identity {identity.id} for user {request.user.id}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            log.error(f"Validation error creating identity: {e.detail}")
            return Response(
                {
                    "success": False,
                    "error": "Validation error",
                    "detail": e.detail if hasattr(e, "detail") else str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            log.error(f"Error creating identity: {str(e)}", exc_info=True)
            return Response(
                {"success": False, "error": "Server error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        """
        Update an identity (full update).
        PUT /api/v1/identities/{id}/
        Body: All identity fields (see IdentitySerializer)
        Returns: 200 OK, updated identity object.
        """
        try:
            pk = kwargs.get("pk")
            identity = get_object_or_404(Identity, id=pk, user=request.user)
            serializer = IdentitySerializer(identity, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            log.error(f"Validation error updating identity: {e.detail}")
            return Response(
                {
                    "success": False,
                    "error": "Validation error",
                    "detail": e.detail if hasattr(e, "detail") else str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Http404:
            return Response(
                {"success": False, "error": "Identity not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            log.error(f"Error updating identity: {str(e)}", exc_info=True)
            return Response(
                {"success": False, "error": "Server error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def partial_update(self, request, *args, **kwargs):
        """
        Partially update an identity.
        PATCH /api/v1/identities/{id}/
        Body: Partial identity fields (see IdentitySerializer)
        Returns: 200 OK, updated identity object.
        """
        try:
            pk = kwargs.get("pk")
            identity = get_object_or_404(Identity, id=pk, user=request.user)
            serializer = IdentitySerializer(identity, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            log.error(f"Validation error during partial update: {e.detail}")
            return Response(
                {
                    "success": False,
                    "error": "Validation error",
                    "detail": e.detail if hasattr(e, "detail") else str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Http404:
            return Response(
                {"success": False, "error": "Identity not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            log.error(f"Server error during partial update: {str(e)}", exc_info=True)
            return Response(
                {"success": False, "error": "Server error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, *args, **kwargs):
        """
        Delete an identity.
        DELETE /api/v1/identities/{id}/
        Returns: 204 No Content.
        """
        try:
            pk = kwargs.get("pk")
            identity = get_object_or_404(Identity, id=pk, user=request.user)
            # Delete the image file if it exists
            if identity.image:
                identity.image.delete()
            identity.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response(
                {"success": False, "error": "Identity not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            log.error(f"Error deleting identity: {str(e)}", exc_info=True)
            return Response(
                {"success": False, "error": "Server error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(
        detail=True,
        methods=["patch", "put"],
        url_path="upload-image",
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_image(self, request, pk=None):
        """
        Upload or update image for an identity.
        PATCH/PUT /api/v1/identities/{id}/upload-image/
        Content-Type: multipart/form-data
        Body: { "image": <file> }
        Returns: 200 OK, updated identity object with image URL.
        """
        try:
            identity = get_object_or_404(Identity, id=pk, user=request.user)

            if "image" not in request.FILES:
                return Response(
                    {"success": False, "error": "No image file provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Delete old image if it exists
            if identity.image:
                identity.image.delete()

            # Save new image
            identity.image = request.FILES["image"]
            identity.save(update_fields=["image"])

            log.info(f"Uploaded image for identity {identity.id}")
            serializer = IdentitySerializer(identity)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404:
            return Response(
                {"success": False, "error": "Identity not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except PermissionDenied:
            return Response(
                {"success": False, "error": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN,
            )
        except Exception as e:
            log.error(f"Error uploading image: {str(e)}", exc_info=True)
            return Response(
                {"success": False, "error": "Server error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(
        detail=True,
        methods=["delete"],
        url_path="delete-image",
    )
    def delete_image(self, request, pk=None):
        """
        Delete image for an identity.
        DELETE /api/v1/identities/{id}/delete-image/
        Returns: 200 OK, updated identity object without image.
        """
        try:
            identity = get_object_or_404(Identity, id=pk, user=request.user)

            if not identity.image:
                return Response(
                    {"success": False, "error": "No image to delete"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Delete the image file
            identity.image.delete()
            identity.image = None
            identity.save(update_fields=["image"])

            log.info(f"Deleted image for identity {identity.id}")
            serializer = IdentitySerializer(identity)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404:
            return Response(
                {"success": False, "error": "Identity not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except PermissionDenied:
            return Response(
                {"success": False, "error": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN,
            )
        except Exception as e:
            log.error(f"Error deleting image: {str(e)}", exc_info=True)
            return Response(
                {"success": False, "error": "Server error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
