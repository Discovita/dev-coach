"""
Management command to generate I Am Statements PDF for a user.

Usage:
    python manage.py generate_i_am_pdf <user_id> [--output <path>]

Examples:
    # Generate PDF for user with ID 123, save to default location
    python manage.py generate_i_am_pdf 123
    
    # Generate PDF for user with ID 123, save to specific location
    python manage.py generate_i_am_pdf 123 --output /tmp/statements.pdf
    
    # Generate PDF using email to look up user
    python manage.py generate_i_am_pdf --email user@example.com
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from services.pdf import PDFService

User = get_user_model()


class Command(BaseCommand):
    """Generate I Am Statements PDF for a specific user."""
    
    help = 'Generate I Am Statements PDF for a specific user'

    def add_arguments(self, parser):
        """
        Define command arguments.
        
        Arguments:
            user_id: The ID of the user to generate the PDF for (positional, optional)
            --email: Email address to look up the user (alternative to user_id)
            --output: Output file path (optional, defaults to ./i-am-statements-<user_id>.pdf)
        """
        parser.add_argument(
            'user_id',
            nargs='?',
            type=str,
            help='The ID of the user to generate the PDF for'
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to look up the user (alternative to user_id)'
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output file path (defaults to ./i-am-statements-<user_id>.pdf)'
        )

    def handle(self, *args, **options):
        """
        Execute the command.
        
        Step-by-step:
        1. Look up the user by ID or email
        2. Generate the PDF using PDFService
        3. Write the PDF to the output file
        4. Print success message
        """
        user_id = options.get('user_id')
        email = options.get('email')
        output_path = options.get('output')
        
        # Validate arguments
        if not user_id and not email:
            raise CommandError('You must provide either a user_id or --email')
        
        if user_id and email:
            raise CommandError('Provide either user_id or --email, not both')
        
        # Look up the user
        try:
            if user_id:
                user = User.objects.get(pk=user_id)
            else:
                user = User.objects.get(email=email)
        except User.DoesNotExist:
            identifier = user_id or email
            raise CommandError(f'User not found: {identifier}')
        
        self.stdout.write(f'Generating PDF for user: {user.id} ({getattr(user, "email", "no email")})')
        
        # Generate the PDF
        try:
            pdf_buffer = PDFService.generate_i_am_statements_pdf(user)
        except ValueError as e:
            raise CommandError(str(e))
        except Exception as e:
            raise CommandError(f'Error generating PDF: {str(e)}')
        
        # Determine output path
        if not output_path:
            user_name = getattr(user, 'name', None) or f'user-{user.id}'
            safe_name = "".join(c for c in user_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '-')[:30]
            output_path = f'./i-am-statements-{safe_name}.pdf'
        
        # Write the PDF to file
        try:
            with open(output_path, 'wb') as f:
                f.write(pdf_buffer.read())
        except IOError as e:
            raise CommandError(f'Error writing PDF to {output_path}: {str(e)}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully generated PDF: {output_path}')
        )
