"""
process_identity_images

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

from apps.test_scenario.utils.delete_identity_image import delete_identity_image
from apps.test_scenario.utils.delete_removed_identity_images import (
    delete_removed_identity_images,
)
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

    delete_removed_identity_images(template, old_template)

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
            delete_identity_image(template["identities"][index])

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
