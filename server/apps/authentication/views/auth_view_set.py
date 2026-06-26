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
    register_via_invite,
    resend_verification,
    reset_password,
    validate_invite,
    verify_email,
)
from apps.authentication.functions.public.reset_password import (
    TokenExpiredError,
    TokenInvalidError,
)
from apps.authentication.functions.public.validate_invite import (
    InviteAcceptedError,
    InviteExpiredError,
    InviteInvalidError,
)
from apps.authentication.functions.public.verify_email import (
    VerificationExpiredError,
    VerificationInvalidError,
)
from apps.authentication.serializers import (
    LoginSerializer,
    RegisterViaInviteSerializer,
)
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
    - POST /api/v1/auth/verify-email/
    - POST /api/v1/auth/resend-verification/
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
        """
        POST /api/v1/auth/register/  — disabled (registration is invite-only).

        Public self-service registration is closed: accounts can only be created
        by accepting an emailed invite (see ``register_via_invite``). This keeps
        the endpoint present (so the route doesn't 404) but refuses to create
        users, closing the door that hiding the UI form alone would leave open.
        """
        return error_response(
            "Registration is invite-only. Please use your invitation link.",
            status_code=status.HTTP_403_FORBIDDEN,
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

    # ------------------------------------------------------------------
    # POST /api/v1/auth/verify-email/
    # ------------------------------------------------------------------
    @decorators.action(
        detail=False,
        methods=["post"],
        permission_classes=[AllowAny],
        url_path="verify-email",
    )
    def verify_email(self, request: Request) -> Response:
        """POST /api/v1/auth/verify-email/  — Confirm an email address."""
        token = request.data.get("token")
        if not token:
            return error_response(AuthErrorMessages.VERIFICATION_INVALID)

        try:
            result = verify_email(token)
            return success_response(result)
        except VerificationInvalidError as e:
            return error_response(str(e))
        except VerificationExpiredError as e:
            return error_response(str(e))
        except Exception:
            log.exception("Unexpected error in verify-email")
            return error_response(AuthErrorMessages.UNEXPECTED_ERROR)

    # ------------------------------------------------------------------
    # POST /api/v1/auth/resend-verification/
    # ------------------------------------------------------------------
    @decorators.action(
        detail=False,
        methods=["post"],
        permission_classes=[AllowAny],
        url_path="resend-verification",
    )
    def resend_verification(self, request: Request) -> Response:
        """POST /api/v1/auth/resend-verification/  — Re-send a verify email."""
        email = request.data.get("email")
        if not email:
            return error_response(AuthErrorMessages.INVALID_EMAIL_FORMAT)

        try:
            result = resend_verification(email)
            return success_response(
                {"message": result["message"], "email_sent": result["email_sent"]}
            )
        except Exception:
            log.exception("Unexpected error in resend-verification for %s", email)
            return error_response(AuthErrorMessages.UNEXPECTED_ERROR)

    # ------------------------------------------------------------------
    # GET /api/v1/auth/invites/{token}
    # ------------------------------------------------------------------
    @decorators.action(
        detail=False,
        methods=["get"],
        permission_classes=[AllowAny],
        url_path=r"invites/(?P<token>[^/.]+)",
    )
    def validate_invite(self, request: Request, token: str = "") -> Response:
        """GET /api/v1/auth/invites/{token} — validate + return the locked email."""
        try:
            result = validate_invite(token)
            return success_response(result)
        except (InviteInvalidError, InviteExpiredError, InviteAcceptedError) as e:
            return error_response(str(e))
        except Exception:
            log.exception("Unexpected error validating invite")
            return error_response(AuthErrorMessages.UNEXPECTED_ERROR)

    # ------------------------------------------------------------------
    # POST /api/v1/auth/register-via-invite/
    # ------------------------------------------------------------------
    @decorators.action(
        detail=False,
        methods=["post"],
        permission_classes=[AllowAny],
        url_path="register-via-invite",
    )
    def register_via_invite(self, request: Request) -> Response:
        """POST /api/v1/auth/register-via-invite — accept an invite + log in."""
        serializer = RegisterViaInviteSerializer(data=request.data)
        if not serializer.is_valid():
            error_msg = serializer.errors.get("password", serializer.errors)
            if isinstance(error_msg, list):
                error_msg = error_msg[0]
            return error_response(error_msg)

        try:
            result = register_via_invite(
                token=serializer.validated_data["token"],
                password=serializer.validated_data["password"],
            )
            return Response({"success": True, **result})
        except (InviteInvalidError, InviteExpiredError, InviteAcceptedError) as e:
            return error_response(str(e))
        except Exception:
            log.exception("Unexpected error in register-via-invite")
            return error_response(AuthErrorMessages.UNEXPECTED_ERROR)
