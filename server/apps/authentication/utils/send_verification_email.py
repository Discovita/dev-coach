"""
Send email-verification emails via AWS SES.
"""

import boto3
from botocore.exceptions import ClientError

from django.conf import settings
from django.template.loader import render_to_string

from apps.authentication.utils.verification_token import (
    TOKEN_EXPIRY_HOURS,
    generate_verification_token,
)
from apps.users.models import User
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


def send_verification_email(user: User) -> bool:
    """
    Generate a verification token and send a verify-email message via AWS SES.

    Args:
        user: User whose email address needs verifying.

    Returns:
        True if the email was sent successfully, False on any SES or
        unexpected error.
    """
    try:
        ses = boto3.client(
            "ses",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )

        token = generate_verification_token(user)
        verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        context = {
            "verify_url": verify_url,
            "expiry_hours": TOKEN_EXPIRY_HOURS,
            "logo_url": f"{settings.FRONTEND_URL}/neovita_logo_small.png",
        }

        html_content = render_to_string("verification_email.html", context)
        text_content = render_to_string("verification_email.txt", context)

        ses.send_email(
            Source=settings.AWS_SES_SOURCE_EMAIL,
            Destination={"ToAddresses": [user.email]},
            Message={
                "Subject": {"Data": "Verify your NeoVita email"},
                "Body": {
                    "Text": {"Data": text_content},
                    "Html": {"Data": html_content},
                },
            },
        )
        log.info("Sent verification email to %s", user.email)
        return True

    except ClientError as e:
        log.error("AWS SES error sending verification to %s: %s", user.email, e)
        return False
    except Exception as e:
        log.error(
            "Unexpected error sending verification email to %s: %s", user.email, e
        )
        return False
