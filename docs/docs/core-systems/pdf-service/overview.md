# PDF Service

## Overview

The PDF Service provides centralized PDF generation capabilities for the application. It uses ReportLab for generating PDF documents and follows a modular generator pattern for different PDF types.

## Architecture

```
server/services/pdf/
├── __init__.py           # Exports PDFService
├── pdf_service.py        # Main service interface
└── generators/
    ├── __init__.py
    └── i_am_statements_pdf.py  # I Am Statements PDF generator
```

## Usage

### In Python Code

```python
from services.pdf import PDFService

# Generate I Am Statements PDF for a user
pdf_buffer = PDFService.generate_i_am_statements_pdf(user)
```

### Via API Endpoint

**Authenticated User (own PDF):**
```
GET /api/v1/identities/download-i-am-statements-pdf/
```

**Admin (any user's PDF):**
```
GET /api/v1/admin/identities/download-i-am-statements-pdf-for-user/?user_id=<id>
```

### Via Management Command

```bash
# Generate PDF for user by ID
python manage.py generate_i_am_pdf <user_id>

# Generate PDF for user by email
python manage.py generate_i_am_pdf --email user@example.com

# Specify output path
python manage.py generate_i_am_pdf <user_id> --output /path/to/output.pdf
```

## I Am Statements PDF

The I Am Statements PDF generator creates a single-page PDF containing:

- **Header**: User name and generation date
- **Identity Cards**: Two-column layout with:
  - Identity name (bold)
  - Category (italicized)
  - I Am Statement (quoted)

### Design Specifications

- **Page Size**: Letter (8.5" x 11")
- **Margins**: 0.5" on all sides
- **Layout**: Two-column table
- **Styling**: Clean, professional appearance with subtle borders

### Data Requirements

The PDF generator requires identities with:
- `state = IdentityState.I_AM_COMPLETE`
- Not in `ARCHIVED` state

If no qualifying identities exist, a `ValueError` is raised.

## Adding New PDF Types

To add a new PDF type:

1. Create a new generator in `generators/`:

```python
# generators/new_pdf_type.py
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate

def generate_new_pdf_type(user) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    # Add content to story
    doc.build(story)
    buffer.seek(0)
    return buffer
```

2. Add method to `PDFService`:

```python
@staticmethod
def generate_new_pdf_type(user: User) -> BytesIO:
    from .generators.new_pdf_type import generate_new_pdf_type
    return generate_new_pdf_type(user)
```

3. Create API endpoint in appropriate ViewSet

4. Create frontend hook and component integration

## Dependencies

- `reportlab>=4.2.5` - PDF generation library
- `Pillow>=10.0.0` - Image processing (if images are included)

## Error Handling

The service raises:
- `ValueError` - When required data is missing (e.g., no completed identities)
- Standard exceptions for I/O errors

API endpoints catch these and return appropriate HTTP responses:
- `400 Bad Request` - For `ValueError`
- `500 Internal Server Error` - For unexpected errors

## Related Documentation

- [Identities API](/docs/api/endpoints/identities.md) - API endpoints for identity management
- [Action Handler System](/docs/core-systems/action-handler/overview.md) - How actions update identity state
