"""
HTTP response helpers for the authentication ViewSet.

These are HTTP-aware utilities called only from views, not from functions.
"""

from typing import TypedDict

from rest_framework import status
from rest_framework.response import Response


class ResponseData(TypedDict, total=False):
    """Type hints for authentication response payloads."""

    success: bool
    message: str
    error: str
    user: dict
    tokens: dict
    email_sent: bool


def error_response(
    message: str, status_code: int = status.HTTP_400_BAD_REQUEST
) -> Response:
    """
    Create a standardized error response.

    Args:
        message: Error message to return.
        status_code: HTTP status code (default: 400).

    Returns:
        Response with ``{"success": false, "error": message}``.
    """
    return Response({"success": False, "error": message}, status=status_code)


def success_response(
    data: ResponseData, status_code: int = status.HTTP_200_OK
) -> Response:
    """
    Create a standardized success response.

    Args:
        data: Response payload (message, user, tokens, etc.).
        status_code: HTTP status code (default: 200).

    Returns:
        Response with ``{"success": true, ...data}``.
    """
    response_data: dict = {"success": True}

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict) and key == "data":
                response_data.update(value)
            else:
                response_data[key] = value

    return Response(response_data, status=status_code)
