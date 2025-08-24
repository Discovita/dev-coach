from rest_framework import viewsets, status, decorators
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User
from apps.authentication.email_service import EmailVerificationService
from apps.authentication.serializer import RegisterSerializer, LoginSerializer
from apps.users.serializer import UserSerializer
from .utils import (
    AuthErrorMessages,
    error_response,
    success_response,
)
from rest_framework.response import Response
from django.db import transaction

from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


class AuthViewSet(viewsets.GenericViewSet):
    """
    ViewSet for authentication-related endpoints.

    Endpoints:
    - register: Create new user account
    - login: Authenticate user and get tokens
    - forgot_password: Initiate password reset
    - reset_password: Complete password reset
    """

    @decorators.action(
        detail=False,
        methods=["post"],
        url_path="register",
        permission_classes=[AllowAny],
    )
    def register(self, request: Request):
        """
        API view to register a new user.
        """
        log.fine("[AuthViewSet]register")
        log.info(
            "[AuthViewSet] register: request data=%s", request.data
        )  # Log the request data
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            error_msg = serializer.errors.get("error", serializer.errors)
            if isinstance(error_msg, list):
                error_msg = error_msg[0]
            return Response(
                {"success": False, "error": error_msg},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated_data = serializer.validated_data
        email = validated_data.get("email")
        password = validated_data.get("password")
        log.fine("[AuthViewSet] register: email=%s", email)

        try:
            with transaction.atomic():
                user = User.objects.create_user(email=email, password=password)
                refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "success": True,
                    "user_id": user.id,
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                }
            )

        except Exception as e:
            log.error(f"Error creating user for email {email}: {e}", exc_info=True)
            return Response(
                {"success": False, "error": f"Unable to create new user: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @decorators.action(
        detail=False,
        methods=["post"],
        url_path="login",
        permission_classes=[AllowAny],
    )
    def login(self, request: Request):
        """
        API view to obtain JWT tokens for existing users.
        """
        log.fine("[AuthViewSet] login")

        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            # Extract error message from serializer errors
            error_msg = serializer.errors.get("non_field_errors", serializer.errors)
            if isinstance(error_msg, list):
                error_msg = error_msg[0]
            elif isinstance(error_msg, dict):
                # Get the first error message from the dict
                first_error = next(iter(error_msg.values()))
                error_msg = (
                    first_error[0] if isinstance(first_error, list) else first_error
                )
            return Response(
                {"success": False, "error": error_msg},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "success": True,
                "user_id": user.id,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            }
        )

    @decorators.action(
        detail=False,
        methods=["post"],
        permission_classes=[AllowAny],
        url_path="forgot-password",
    )
    def forgot_password(self, request: Request):
        """
        Initiate password reset process.
        """
        log.fine("[AuthViewSet.forgot_password]")
        email = request.data.get("email")
        if not email:
            log.warn("[AuthViewSet.forgot_password] No email provided in request")
            return error_response(AuthErrorMessages.INVALID_EMAIL_FORMAT)

        try:
            user = User.objects.get(email=email)
            log.info(f"[AuthViewSet.forgot_password] Found user for email {email}")

            EmailVerificationService.generate_verification_token(user)
            log.info(
                f"[AuthViewSet.forgot_password] Generated verification token for user {email}"
            )

            email_sent = EmailVerificationService.send_password_reset_email(user)

            if email_sent:
                log.info(
                    f"[AuthViewSet.forgot_password] Successfully sent password reset email to {email}"
                )
                return success_response({"message": "Password reset email sent"})

            log.error(
                f"[AuthViewSet.forgot_password] Failed to send password reset email to {email}"
            )
            return error_response(AuthErrorMessages.EMAIL_SEND_FAILED)

        except User.DoesNotExist:
            log.info(f"[AuthViewSet.forgot_password] No user found for email {email}")
            return success_response(
                {"message": "If an account exists, a password reset email will be sent"}
            )
        except Exception as e:
            log.error(
                f"[AuthViewSet.forgot_password] Unexpected error during password reset: {e}"
            )
            return error_response("An unexpected error occurred")

    @decorators.action(
        detail=False,
        methods=["post"],
        permission_classes=[AllowAny],
        url_path="reset-password",
    )
    def reset_password(self, request: Request):
        """
        Reset password using token.
        """
        log.fine("[AuthViewSet.reset_password]")
        token = request.data.get("token")
        new_password = request.data.get("password")

        if not token or not new_password:
            log.warn(
                "[AuthViewSet.reset_password] Missing token or new password in request"
            )
            return error_response("Token and new password are required")

        try:
            user = User.objects.get(verification_token=token)
            log.info(
                f"[AuthViewSet.reset_password] Found user for reset token: {user.email}"
            )

            if EmailVerificationService.is_token_expired(user):
                log.warn(
                    f"[AuthViewSet.reset_password] Expired token for user {user.email}"
                )
                return error_response(AuthErrorMessages.VERIFICATION_EXPIRED)

            # Update password
            user.set_password(new_password)
            user.save()
            log.info(
                f"[AuthViewSet.reset_password] Successfully updated password for user {user.email}"
            )

            # Clear verification token
            user.verification_token = ""
            user.email_verification_sent_at = None
            user.save()
            log.info(
                f"[AuthViewSet.reset_password] Cleared verification token for user {user.email}"
            )

            return success_response({"message": "Password updated successfully"})

        except User.DoesNotExist:
            log.warn(
                "[AuthViewSet.reset_password] Invalid or unknown verification token"
            )
            return error_response(AuthErrorMessages.VERIFICATION_INVALID)
        except Exception as e:
            log.error(
                f"[AuthViewSet.reset_password] Unexpected error during password reset: {e}"
            )
            return error_response("An unexpected error occurred")
