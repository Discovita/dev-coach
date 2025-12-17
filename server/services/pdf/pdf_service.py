"""
PDF Service

Provides a centralized interface for PDF generation operations.
Uses generator modules in the generators/ subdirectory for specific PDF types.
"""

from io import BytesIO
from django.contrib.auth import get_user_model
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")

User = get_user_model()


class PDFService:
    """
    Service class for PDF generation operations.
    
    Usage:
        from services.pdf import PDFService
        
        # Generate I Am Statements PDF for a user
        pdf_buffer = PDFService.generate_i_am_statements_pdf(user)
    """

    @staticmethod
    def generate_i_am_statements_pdf(user: User) -> BytesIO:
        """
        Generate a PDF containing the user's I Am Statements.
        
        Args:
            user: The User instance to generate the PDF for.
            
        Returns:
            BytesIO buffer containing the generated PDF.
            
        Raises:
            ValueError: If the user has no completed identities.
        """
        from .generators.i_am_statements_pdf import generate_i_am_statements_pdf
        
        log.info(f"Generating I Am Statements PDF for user {user.id}")
        
        pdf_buffer = generate_i_am_statements_pdf(user)
        
        log.info(f"Successfully generated I Am Statements PDF for user {user.id}")
        
        return pdf_buffer
