"""
Handle image uploads and deletions for identity images in scenario templates.

Processes ``request.FILES`` named ``identity_<index>_image`` and injects
the resulting S3 URLs into ``template["identities"][index]["image"]``.
Also handles deletion of images that were present in a previous template
version but absent in the new one.

See: apps/test_scenario/utils/__init__.py
"""

import os
import re
import uuid

from django.core.files.storage import default_storage

from apps.test_scenario.utils.extract_s3_key import extract_s3_key_from_url
from services.logger import configure_logging

log = configure_logging(__name__)


def process_identity_images(
    request, template: dict, old_template: dict | None = None
) -> dict:
    """
    Process image file uploads and deletions for a scenario template.

    Args:
        request: The Django/DRF request (used for ``request.FILES``).
        template: The current template dict (mutated in place).
        old_template: The previous template dict, used to detect removed images.

    Returns:
        The (possibly mutated) *template* dict.
    """
    if "identities" not in template or not template["identities"]:
        return template

    _delete_removed_images(template, old_template)

    if not request.FILES:
        return template

    image_files: dict[int, object] = {}
    for key in request.FILES.keys():
        match = re.match(r"identity_(\d+)_image", key)
        if match:
            image_files[int(match.group(1))] = request.FILES[key]

    if not image_files:
        return template

    for index, image_file in image_files.items():
        if index >= len(template["identities"]):
            log.warning(
                f"Image file for identity index {index} but only "
                f"{len(template['identities'])} identities exist"
            )
            continue

        try:
            _delete_old_identity_image(template["identities"][index])

            uuid_dir = str(uuid.uuid4())
            full_path = os.path.join(uuid_dir, image_file.name).replace("\\", "/")
            saved_path = default_storage.save(full_path, image_file)
            image_url = default_storage.url(saved_path)

            template["identities"][index]["image"] = image_url
        except Exception as e:
            log.error(
                f"Error processing image for identity at index {index}: {e}",
                exc_info=True,
            )

    return template


def _delete_removed_images(template: dict, old_template: dict | None) -> None:
    """Delete S3 objects for identities whose image was removed between versions."""
    if not old_template or "identities" not in old_template:
        return

    for index, new_identity in enumerate(template["identities"]):
        if index >= len(old_template["identities"]):
            break
        old_url = old_template["identities"][index].get("image")
        new_url = new_identity.get("image")
        if old_url and not new_url:
            key = extract_s3_key_from_url(old_url)
            if key:
                try:
                    default_storage.delete(key)
                except Exception as e:
                    log.warning(f"Failed to delete removed image at index {index}: {e}")


def _delete_old_identity_image(identity_data: dict) -> None:
    """Delete the existing image for an identity before replacing it."""
    old_url = identity_data.get("image")
    if not old_url:
        return
    key = extract_s3_key_from_url(old_url)
    if key:
        try:
            default_storage.delete(key)
        except Exception as e:
            log.warning(f"Failed to delete old identity image: {e}")
