"""
Identity admin configuration.

Exports:
    IdentityAdmin: Django admin for the Identity model.
    IdentityImageChatAdmin: Django admin for the IdentityImageChat model.
"""

from apps.identities.admin.identity_admin import IdentityAdmin
from apps.identities.admin.identity_image_chat_admin import IdentityImageChatAdmin

__all__ = [
    "IdentityAdmin",
    "IdentityImageChatAdmin",
]
