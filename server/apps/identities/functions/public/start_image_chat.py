"""
Start Image Chat (Public)

User-facing function to start a new image generation chat session.
"""

import base64
import tempfile
import os

from rest_framework.response import Response
from rest_framework import status

from apps.identities.models import Identity
from apps.reference_images.models import ReferenceImage
from apps.users.models import User
from services.image_generation.orchestration import start_identity_image_chat
from services.logger import configure_logging

log = configure_logging(__name__)


def start_image_chat(
    user: User,
    identity_id: str,
    additional_prompt: str = "",
) -> Response:
    """
    Start a new image generation chat for the authenticated user.

    Creates a new Gemini chat session, generates the initial image,
    and stores the chat history for future edits.

    Args:
        user: The authenticated user
        identity_id: UUID of the identity to generate for
        additional_prompt: Optional extra instructions

    Returns:
        Response with image_base64, identity_id, identity_name

    Raises:
        DRF exceptions for validation errors (400, 404, 500)
    """
    from rest_framework.exceptions import NotFound, ValidationError

    # Validate identity exists and belongs to user
    try:
        identity = Identity.objects.get(id=identity_id, user=user)
    except Identity.DoesNotExist:
        raise NotFound(f"Identity {identity_id} not found")

    # Get reference images
    reference_images = list(ReferenceImage.objects.filter(user_id=user.id))
    if not reference_images:
        raise ValidationError(
            f"No reference images found for user {user.id}. "
            "Reference images are required for image generation."
        )

    # Start the chat session
    try:
        pil_image, chat_record = start_identity_image_chat(
            identity=identity,
            reference_images=reference_images,
            user=user,
            additional_prompt=additional_prompt,
        )
    except ValueError as e:
        raise ValidationError(str(e))
    except Exception as e:
        log.error(f"Image generation failed: {e}", exc_info=True)
        from rest_framework.exceptions import APIException

        raise APIException(f"Image generation failed: {str(e)}")

    if not pil_image:
        from rest_framework.exceptions import APIException

        raise APIException("Image generation failed - no image was generated")

    # Convert PIL image to base64
    image_base64 = _pil_to_base64(pil_image)

    return Response(
        {
            "image_base64": image_base64,
            "identity_id": str(identity.id),
            "identity_name": identity.name,
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
