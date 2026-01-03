"""
Admin Identity ViewSet

Provides admin-only endpoints for identity operations, including
generating PDFs for specific users and generating identity images.
"""

from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.http import FileResponse
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from io import BytesIO
import base64

from apps.identities.models import Identity
from apps.identities.serializer import IdentitySerializer
from apps.reference_images.models import ReferenceImage
from services.image_generation.orchestration import generate_identity_image
from services.logger import configure_logging
from services.pdf import PDFService

log = configure_logging(__name__, log_level="INFO")

User = get_user_model()


class AdminIdentityViewSet(viewsets.GenericViewSet):
    """
    Admin-only endpoints for identity operations.
    
    Supported operations:
    - download_i_am_statements_pdf_for_user: GET /api/v1/admin/identities/download-i-am-statements-pdf-for-user/?user_id=<id>
    - generate_image: POST /api/v1/admin/identities/generate-image/
    - save_generated_image: POST /api/v1/admin/identities/save-generated-image/
    """
    
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @action(
        detail=False,
        methods=["get"],
        url_path="download-i-am-statements-pdf-for-user",
        permission_classes=[IsAdminUser],
    )
    def download_i_am_statements_pdf_for_user(self, request):
        """
        Download a PDF containing I Am Statements for a specific user (admin only).
        GET /api/v1/admin/identities/download-i-am-statements-pdf-for-user/?user_id=<id>
        
        Query parameters:
        - user_id (required): The ID of the user to generate the PDF for.
        
        Returns: PDF file download.
        """
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response(
                {"success": False, "error": "user_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            target_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            log.error(f"User with id {user_id} not found")
            return Response(
                {"success": False, "error": f"User with id {user_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        try:
            pdf_buffer = PDFService.generate_i_am_statements_pdf(target_user)
            
            # Create filename with user identifier
            user_name = getattr(target_user, 'name', None) or f'user-{user_id}'
            safe_name = "".join(c for c in user_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '-')[:30]  # Limit length
            filename = f"i-am-statements-{safe_name}.pdf"
            
            response = FileResponse(
                pdf_buffer,
                content_type='application/pdf',
                as_attachment=True,
                filename=filename,
            )
            
            log.info(f"Admin {request.user.id} downloaded I Am Statements PDF for user {target_user.id}")
            return response
            
        except ValueError as e:
            log.warning(f"Cannot generate PDF for user {target_user.id}: {str(e)}")
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            log.error(f"Error generating PDF: {str(e)}", exc_info=True)
            return Response(
                {"success": False, "error": "Server error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    @action(
        detail=False,
        methods=["POST"],
        url_path="generate-image",
        permission_classes=[IsAdminUser],
    )
    def generate_image(self, request):
        """
        Generate an identity image using Gemini.
        
        POST /api/v1/admin/identities/generate-image/
        Body (JSON):
        - identity_id: UUID of the identity
        - user_id: UUID of the user (for reference images)
        - additional_prompt: Extra instructions (optional)
        - save_to_identity: Whether to save to identity (default: false)
        
        Returns: Base64 encoded image and optionally updated identity
        """
        identity_id = request.data.get("identity_id")
        user_id = request.data.get("user_id")
        additional_prompt = request.data.get("additional_prompt", "")
        should_save = request.data.get("save_to_identity", False)
        
        if not identity_id or not user_id:
            return Response(
                {"error": "identity_id and user_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Fetch identity
        try:
            identity = Identity.objects.get(id=identity_id)
        except Identity.DoesNotExist:
            return Response(
                {"error": f"Identity {identity_id} not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Fetch reference images for the user
        reference_images = list(ReferenceImage.objects.filter(user_id=user_id))
        if not reference_images:
            return Response(
                {"error": f"No reference images found for user {user_id}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Generate the image
            pil_image = generate_identity_image(
                identity=identity,
                reference_images=reference_images,
                additional_prompt=additional_prompt,
            )
            
            if not pil_image:
                return Response(
                    {"error": "Image generation failed - no image was generated"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Convert Gemini image to bytes
            # Gemini's as_image() returns a special image type that saves differently
            import tempfile
            import os as temp_os
            
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            try:
                # Gemini image.save() takes just a path
                pil_image.save(tmp_path)
                
                # Read the bytes back
                with open(tmp_path, "rb") as f:
                    image_bytes = f.read()
            finally:
                # Clean up temp file
                if temp_os.path.exists(tmp_path):
                    temp_os.unlink(tmp_path)
            
            # Encode as base64 for response
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            
            response_data = {
                "success": True,
                "image_base64": image_base64,
            }
            
            # Optionally save to identity
            if should_save:
                filename = f"identity_{identity_id}.png"
                identity.image.save(filename, ContentFile(image_bytes))
                identity.save()
                response_data["identity"] = IdentitySerializer(identity).data
            
            return Response(response_data)
            
        except Exception as e:
            log.error(f"Image generation failed: {e}", exc_info=True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(
        detail=False,
        methods=["POST"],
        url_path="save-generated-image",
        permission_classes=[IsAdminUser],
    )
    def save_generated_image(self, request):
        """
        Save a previously generated image to an identity.
        
        POST /api/v1/admin/identities/save-generated-image/
        Body (JSON):
        - identity_id: UUID of the identity
        - image_base64: Base64 encoded image data
        
        Returns: Updated identity
        """
        identity_id = request.data.get("identity_id")
        image_base64 = request.data.get("image_base64")
        
        if not identity_id or not image_base64:
            return Response(
                {"error": "identity_id and image_base64 are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            identity = Identity.objects.get(id=identity_id)
        except Identity.DoesNotExist:
            return Response(
                {"error": f"Identity {identity_id} not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            image_bytes = base64.b64decode(image_base64)
            filename = f"identity_{identity_id}.png"
            identity.image.save(filename, ContentFile(image_bytes))
            identity.save()
            
            return Response({
                "success": True,
                "identity": IdentitySerializer(identity).data
            })
            
        except Exception as e:
            log.error(f"Failed to save image: {e}", exc_info=True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
