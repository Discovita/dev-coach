"""
Admin Identity ViewSet

Provides admin-only endpoints for identity operations, including
generating PDFs for specific users.
"""

from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.http import FileResponse
from django.contrib.auth import get_user_model
from services.logger import configure_logging
from services.pdf import PDFService

log = configure_logging(__name__, log_level="INFO")

User = get_user_model()


class AdminIdentityViewSet(viewsets.GenericViewSet):
    """
    Admin-only endpoints for identity operations.
    
    Supported operations:
    - download_i_am_statements_pdf_for_user: GET /api/v1/admin/identities/download-i-am-statements-pdf-for-user/?user_id=<id>
    """

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
