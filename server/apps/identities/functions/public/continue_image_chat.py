"""
Continue Image Chat (Public)

User-facing function to continue an image chat session.
"""

import base64
import tempfile
import os

from rest_framework.response import Response
from rest_framework import status

from apps.reference_images.models import ReferenceImage
from apps.users.models import User
from services.image_generation.orchestration import continue_identity_image_chat
from services.logger import configure_logging

log = configure_logging(__name__)


def continue_image_chat(
    user: User,
    edit_prompt: str,
) -> Response:
    """
    Continue an existing image chat for the authenticated user.

    Loads the user's existing chat session, sends the edit prompt,
    and returns the new generated image.

    Args:
        user: The authenticated user
        edit_prompt: The edit instruction

    Returns:
        Response with image_base64, identity_id, identity_name

    Raises:
        DRF exceptions for validation errors (400, 404, 500)
    """
    from rest_framework.exceptions import ValidationError, APIException

    # Optionally get reference images (include with edit if available)
    reference_images = list(ReferenceImage.objects.filter(user_id=user.id))

    # Continue the chat session
    try:
        pil_image, chat_record = continue_identity_image_chat(
            user=user,
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
