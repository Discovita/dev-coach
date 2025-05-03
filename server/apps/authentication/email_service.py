"""
Authentication models for email verification and token management.
This module contains functionality for managing authentication flows.
"""

from django.conf import settings
from django.template.loader import render_to_string
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import secrets
from apps.users.models import User

from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


class EmailVerificationService:
    """
    Service class for handling email verification flows.

    Methods:
    - generate_verification_token: Creates a new verification token
    - is_token_expired: Checks if a token has expired
    - send_password_reset_email: Sends password reset email via AWS SES
    """

    @staticmethod
    def generate_verification_token(user: User) -> str:
        """
        Generate a new verification token for a user.

        Args:
            user: User to generate token for

        Returns:
            str: Generated token
        """
        try:
            user.verification_token = secrets.token_hex(32)
            user.email_verification_sent_at = datetime.now().astimezone()
            user.save()
            log.info(
                f"[EmailVerificationService.generate_verification_token] Generated new token for user {user.email}"
            )
            return user.verification_token
        except Exception as e:
            log.error(
                f"[EmailVerificationService.generate_verification_token] Failed to generate token for user {user.email}: {e}"
            )
            raise

    @staticmethod
    def is_token_expired(user: User) -> bool:
        """
        Check if the user's verification token has expired.
        """

        if not user.email_verification_sent_at:
            log.warn(
                f"[EmailVerificationService.is_token_expired] No verification timestamp for user {user.email}"
            )
            return True

        expiry_time = user.email_verification_sent_at + timedelta(hours=24)
        is_expired = datetime.now().astimezone() > expiry_time

        if is_expired:
            log.warn(
                f"[EmailVerificationService.is_token_expired] Token expired for user {user.email}"
            )
        else:
            log.info(
                f"[EmailVerificationService.is_token_expired] Token still valid for user {user.email}"
            )

        return is_expired

    @staticmethod
    def send_password_reset_email(user: User) -> bool:
        """
        Send password reset email using AWS SES.
        """
        try:
            log.info(
                f"[EmailVerificationService.send_password_reset_email] Initializing AWS SES client for user {user.email}"
            )
            ses = boto3.client(
                "ses",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
            )

            # Generate verification token and URL
            log.info(
                f"[EmailVerificationService.send_password_reset_email] Generating verification token for user {user.email}"
            )
            token = EmailVerificationService.generate_verification_token(user)
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"

            # Render both HTML and text templates
            log.info(
                f"[EmailVerificationService.send_password_reset_email] Rendering email templates for user {user.email}"
            )
            html_content = render_to_string(
                "password_reset_email.html",
                {
                    "reset_url": reset_url,
                    "expiry_hours": 24,
                },
            )
            text_content = render_to_string(
                "password_reset_email.txt",
                {
                    "reset_url": reset_url,
                    "expiry_hours": 24,
                },
            )

            log.info(
                f"[EmailVerificationService.send_password_reset_email] Sending email via SES to {user.email}"
            )
            ses.send_email(
                Source=settings.AWS_SES_SOURCE_EMAIL,
                Destination={"ToAddresses": [user.email]},
                Message={
                    "Subject": {"Data": "Reset Your Password - Discovita"},
                    "Body": {
                        "Text": {"Data": text_content},
                        "Html": {"Data": html_content},
                    },
                },
            )
            log.info(
                f"[EmailVerificationService.send_password_reset_email] Successfully sent password reset email to {user.email}"
            )
            return True
        except ClientError as e:
            log.error(
                f"[EmailVerificationService.send_password_reset_email] AWS SES error sending email to {user.email}: {str(e)}"
            )
            return False
        except Exception as e:
            log.error(
                f"[EmailVerificationService.send_password_reset_email] Unexpected error sending email to {user.email}: {str(e)}"
            )
            return False
