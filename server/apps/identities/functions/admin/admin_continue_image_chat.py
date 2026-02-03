"""
Continue Image Chat (Admin)

Admin function to continue an image chat session for any user.
"""

import base64
import tempfile
import os

from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

from apps.reference_images.models import ReferenceImage
from services.image_generation.orchestration import continue_identity_image_chat
from services.logger import configure_logging

log = configure_logging(__name__)

User = get_user_model()


def admin_continue_image_chat(
    user_id: str,
    edit_prompt: str,
) -> Response:
    """
    Continue an existing image chat for a specified user (admin only).

    Loads the user's existing chat session, sends the edit prompt,
    and returns the new generated image.

    Args:
        user_id: UUID of the target user
        edit_prompt: The edit instruction

    Returns:
        Response with image_base64, identity_id, identity_name

    Raises:
        DRF exceptions for validation errors (400, 404, 500)
    """
    from rest_framework.exceptions import NotFound, ValidationError, APIException

    # Validate user exists
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise NotFound(f"User {user_id} not found")

    # Optionally get reference images (include with edit if available)
    reference_images = list(ReferenceImage.objects.filter(user_id=user_id))

    # Continue the chat session
    try:
        pil_image, chat_record = continue_identity_image_chat(
            user=target_user,
            edit_prompt=edit_prompt,
            reference_images=reference_images if reference_images else None,
        )
    except ValueError as e:
        raise ValidationError(str(e))
    except Exception as e:
        log.error(f"Image edit failed: {e}", exc_info=True)
        raise APIException(f"Image edit failed: {str(e)}")

    if not pil_image:
        raise APIException("Image edit failed - no image was generated")

    # Convert PIL image to base64
    image_base64 = _pil_to_base64(pil_image)

    identity = chat_record.identity

    return Response(
        {
            "image_base64": image_base64,
            "identity_id": str(identity.id) if identity else None,
            "identity_name": identity.name if identity else None,
        },
        status=status.HTTP_200_OK,
    )


def _pil_to_base64(pil_image) -> str:
    """Convert a PIL/Gemini image to base64 string."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        tmp_path = tmp_file.name

    try:
        pil_image.save(tmp_path)
        with open(tmp_path, "rb") as f:
            image_bytes = f.read()
        return base64.b64encode(image_bytes).decode("utf-8")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
