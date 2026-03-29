"""
Authentication serializers.

Input validation for registration, login, and LTI launch requests.
"""

from apps.authentication.serializers.login_serializer import LoginSerializer
from apps.authentication.serializers.register_serializer import RegisterSerializer
from apps.authentication.serializers.resource_link_serializer import (
    ResourceLinkSerializer,
)

__all__ = [
    "LoginSerializer",
    "RegisterSerializer",
    "ResourceLinkSerializer",
]
