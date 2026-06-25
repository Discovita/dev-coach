"""
Start Image Chat (Admin)

Admin function to start a new image generation chat session for any user.
"""

import base64
import os
import tempfile

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response

from apps.identities.models import Identity
from apps.reference_images.models import ReferenceImage
from services.image_generation import ImageGenerationError
from services.image_generation.orchestration import start_identity_image_chat
from services.logger import configure_logging

log = configure_logging(__name__)

User = get_user_model()


def admin_start_image_chat(
    identity_id: str,
    user_id: str,
    additional_prompt: str = "",
) -> Response:
    """
    Start a new image generation chat for a specified user (admin only).

    Creates a new Gemini chat session, generates the initial image,
    and stores the chat history for future edits.

    Args:
        identity_id: UUID of the identity to generate for
        user_id: UUID of the target user
        additional_prompt: Optional extra instructions

    Returns:
        Response with image_base64, identity_id, identity_name

    Raises:
        DRF exceptions for validation errors (400, 404, 500)
    """
    from rest_framework.exceptions import NotFound, ValidationError

    # Validate identity exists
    try:
        identity = Identity.objects.get(id=identity_id)
    except Identity.DoesNotExist:
        raise NotFound(f"Identity {identity_id} not found")

    # Validate user exists
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise NotFound(f"User {user_id} not found")

    # Get reference images
    reference_images = list(ReferenceImage.objects.filter(user_id=user_id))
    if not reference_images:
        raise ValidationError(
            f"No reference images found for user {user_id}. "
            "Reference images are required for image generation."
        )

    # Start the chat session. Errors return the same structured,
    # human-readable shape as the public endpoint ({error, error_code,
    # details}) so the frontend renders a friendly banner — never raw JSON.
    try:
        pil_image, chat_record = start_identity_image_chat(
            identity=identity,
            reference_images=reference_images,
            user=target_user,
            additional_prompt=additional_prompt,
        )
    except ValueError as e:
        raise ValidationError(str(e))
    except ImageGenerationError as e:
        log.warning(f"Image generation error: {e.error_code} - {e.message}")
        return Response(
            {"error": e.message, "error_code": e.error_code, "details": e.details},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        log.error(f"Image generation failed: {e}", exc_info=True)
        return Response(
            {
                "error": "Something went wrong while generating your image. Please try again.",
                "error_code": "UNKNOWN",
                "details": None,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if not pil_image:
        return Response(
            {
                "error": "No image was generated. Please try a different prompt.",
                "error_code": "EMPTY_RESPONSE",
                "details": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

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
