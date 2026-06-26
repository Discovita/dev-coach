"""
Send invite (magic-link) emails via AWS SES.
"""

import boto3
from botocore.exceptions import ClientError

from django.conf import settings
from django.template.loader import render_to_string

from apps.authentication.models import INVITE_EXPIRY_DAYS, Invite
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


def send_invite_email(invite: Invite) -> bool:
    """
    Send the magic-link invitation for ``invite`` via AWS SES.

    Args:
        invite: The Invite to send (its current token is used in the link).

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

        invite_url = f"{settings.FRONTEND_URL}/invite/{invite.token}"
        context = {
            "invite_url": invite_url,
            "expiry_days": INVITE_EXPIRY_DAYS,
            "logo_url": f"{settings.FRONTEND_URL}/neovita_logo_small.png",
        }

        html_content = render_to_string("invite_email.html", context)
        text_content = render_to_string("invite_email.txt", context)

        ses.send_email(
            Source=settings.AWS_SES_SOURCE_EMAIL,
            Destination={"ToAddresses": [invite.email]},
            Message={
                "Subject": {"Data": "You're invited to NeoVita"},
                "Body": {
                    "Text": {"Data": text_content},
                    "Html": {"Data": html_content},
                },
            },
        )
        log.info("Sent invite email to %s", invite.email)
        return True

    except ClientError as e:
        log.error("AWS SES error sending invite to %s: %s", invite.email, e)
        return False
    except Exception as e:
        log.error("Unexpected error sending invite email to %s: %s", invite.email, e)
        return False
