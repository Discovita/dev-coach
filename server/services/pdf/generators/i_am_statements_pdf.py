"""
I Am Statements PDF Generator

Generates a single-page PDF containing all of a user's identities
with their I Am statements.
"""

from io import BytesIO
from datetime import datetime
from django.contrib.auth import get_user_model
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)
from apps.identities.models import Identity
from enums.identity_state import IdentityState
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")

User = get_user_model()


def generate_i_am_statements_pdf(user: User) -> BytesIO:
    """
    Generate a PDF containing the user's I Am Statements.
    
    The PDF is designed to fit on a single page and includes:
    - Header with user name and date
    - Two-column layout of identity cards
    - Each card shows: identity name, category, and I Am statement
    
    Args:
        user: The User instance to generate the PDF for.
        
    Returns:
        BytesIO buffer containing the generated PDF.
        
    Raises:
        ValueError: If the user has no completed identities.
    """
    # Fetch completed identities
    identities = Identity.objects.filter(
        user=user,
        state=IdentityState.I_AM_COMPLETE,
    ).exclude(
        state=IdentityState.ARCHIVED
    ).order_by("created_at")
    
    if not identities.exists():
        log.warning(f"No completed identities found for user {user.id}")
        raise ValueError("No completed identities found for this user.")
    
    # Create PDF buffer
    buffer = BytesIO()
    
    # Create document with tight margins for single-page fit
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )
    
    # Build the story (list of flowables)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles for compact display
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=6,
        textColor=colors.HexColor('#1a1a1a'),
        alignment=1,  # Center
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=12,
        textColor=colors.HexColor('#666666'),
        alignment=1,  # Center
    )
    
    identity_name_style = ParagraphStyle(
        'IdentityName',
        parent=styles['Heading3'],
        fontSize=11,
        spaceAfter=2,
        textColor=colors.HexColor('#1a1a1a'),
        leading=13,
    )
    
    category_style = ParagraphStyle(
        'Category',
        parent=styles['Normal'],
        fontSize=8,
        spaceAfter=4,
        textColor=colors.HexColor('#888888'),
        fontName='Helvetica-Oblique',
    )
    
    statement_style = ParagraphStyle(
        'Statement',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#333333'),
        leading=11,
    )
    
    # Header
    user_name = getattr(user, 'name', None) or getattr(user, 'email', 'User')
    story.append(Paragraph("My Identities & I Am Statements", title_style))
    story.append(Paragraph(
        f"{user_name} • {datetime.now().strftime('%B %d, %Y')}",
        subtitle_style
    ))
    story.append(Spacer(1, 0.1 * inch))
    
    # Build identity cards
    identity_cards = []
    for identity in identities:
        card_content = []
        
        # Identity name
        card_content.append(Paragraph(identity.name, identity_name_style))
        
        # Category (formatted nicely)
        if identity.category:
            category_display = identity.category.replace('_', ' ').title()
            card_content.append(Paragraph(category_display, category_style))
        
        # I Am Statement
        if identity.i_am_statement:
            # Clean up the statement (remove markdown formatting if any)
            statement = identity.i_am_statement.replace('**', '').replace('*', '')
            card_content.append(Paragraph(f'"{statement}"', statement_style))
        
        identity_cards.append(card_content)
    
    # Arrange cards in two columns using a table
    # Group cards into pairs for two-column layout
    table_data = []
    for i in range(0, len(identity_cards), 2):
        row = []
        
        # First card in row
        card1_content = identity_cards[i]
        row.append(card1_content)
        
        # Second card in row (if exists)
        if i + 1 < len(identity_cards):
            card2_content = identity_cards[i + 1]
            row.append(card2_content)
        else:
            row.append([])  # Empty cell
        
        table_data.append(row)
    
    # Calculate column widths
    page_width = letter[0] - inch  # Account for margins
    col_width = page_width / 2 - 0.1 * inch
    
    # Create table
    if table_data:
        table = Table(
            table_data,
            colWidths=[col_width, col_width],
        )
        
        table.setStyle(TableStyle([
            # Cell padding
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            # Vertical alignment
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            # Light border for cards
            ('BOX', (0, 0), (0, -1), 0.5, colors.HexColor('#e0e0e0')),
            ('BOX', (1, 0), (1, -1), 0.5, colors.HexColor('#e0e0e0')),
            # Row separators
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#e0e0e0')),
        ]))
        
        story.append(table)
    
    # Build the PDF
    doc.build(story)
    
    # Reset buffer position to beginning
    buffer.seek(0)
    
    return buffer
