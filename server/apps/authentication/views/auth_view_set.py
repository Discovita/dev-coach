"""
AuthViewSet — thin HTTP layer for authentication endpoints.

All business logic is delegated to ``functions/public/``.
"""

from rest_framework import decorators, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from apps.authentication.functions.public import (
    forgot_password,
    login_user,
    register_user,
    reset_password,
)
from apps.authentication.functions.public.reset_password import (
    TokenExpiredError,
    TokenInvalidError,
)
from apps.authentication.serializers import LoginSerializer, RegisterSerializer
from apps.authentication.utils import (
    AuthErrorMessages,
    error_response,
    success_response,
)
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


class AuthViewSet(viewsets.GenericViewSet):
    """
    Public authentication endpoints (all ``AllowAny``).

    Endpoints:
    - POST /api/v1/auth/register/
    - POST /api/v1/auth/login/
    - POST /api/v1/auth/forgot-password/
    - POST /api/v1/auth/reset-password/
    """

    # ------------------------------------------------------------------
    # POST /api/v1/auth/register/
    # ------------------------------------------------------------------
    @decorators.action(
        detail=False,
        methods=["post"],
        url_path="register",
        permission_classes=[AllowAny],
    )
    def register(self, request: Request) -> Response:
        """POST /api/v1/auth/register/  — Create a new user account."""
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            error_msg = serializer.errors.get("error", serializer.errors)
            if isinstance(error_msg, list):
                error_msg = error_msg[0]
            return error_response(error_msg)

        try:
            result = register_user(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )
            return Response({"success": True, **result})
        except Exception as e:
            log.error("Registration failed for %s: %s", request.data.get("email"), e)
            return error_response(
                AuthErrorMessages.UNEXPECTED_ERROR,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # ------------------------------------------------------------------
    # POST /api/v1/auth/login/
    # ------------------------------------------------------------------
    @decorators.action(
        detail=False,
        methods=["post"],
        url_path="login",
        permission_classes=[AllowAny],
    )
    def login(self, request: Request) -> Response:
        """POST /api/v1/auth/login/  — Authenticate and return JWT tokens."""
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            error_msg = serializer.errors.get("non_field_errors", serializer.errors)
            if isinstance(error_msg, list):
                error_msg = error_msg[0]
            elif isinstance(error_msg, dict):
                first_error = next(iter(error_msg.values()))
                error_msg = (
                    first_error[0] if isinstance(first_error, list) else first_error
                )
            return error_response(error_msg)

        result = login_user(serializer.validated_data["user"])
        return Response({"success": True, **result})

    # ------------------------------------------------------------------
    # POST /api/v1/auth/forgot-password/
    # ------------------------------------------------------------------
    @decorators.action(
        detail=False,
        methods=["post"],
        permission_classes=[AllowAny],
        url_path="forgot-password",
    )
    def forgot_password(self, request: Request) -> Response:
        """POST /api/v1/auth/forgot-password/  — Initiate password reset."""
        email = request.data.get("email")
        if not email:
            return error_response(AuthErrorMessages.INVALID_EMAIL_FORMAT)

        try:
            result = forgot_password(email)
            return success_response({"message": result["message"]})
        except RuntimeError as e:
            return error_response(str(e))
        except Exception:
            log.exception("Unexpected error in forgot-password for %s", email)
            return error_response(AuthErrorMessages.UNEXPECTED_ERROR)

    # ------------------------------------------------------------------
    # POST /api/v1/auth/reset-password/
    # ------------------------------------------------------------------
    @decorators.action(
        detail=False,
        methods=["post"],
        permission_classes=[AllowAny],
        url_path="reset-password",
    )
    def reset_password(self, request: Request) -> Response:
        """POST /api/v1/auth/reset-password/  — Complete password reset."""
        token = request.data.get("token")
        new_password = request.data.get("password")

        if not token or not new_password:
            return error_response("Token and new password are required")

        try:
            result = reset_password(token, new_password)
            return success_response(result)
        except TokenInvalidError as e:
            return error_response(str(e))
        except TokenExpiredError as e:
            return error_response(str(e))
        except Exception:
            log.exception("Unexpected error in reset-password")
            return error_response(AuthErrorMessages.UNEXPECTED_ERROR)
