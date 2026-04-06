"""
delete_removed_identity_images

Delete S3 objects for identity images that were removed between template versions.
"""

from django.core.files.storage import default_storage

from apps.test_scenario.utils.extract_s3_key import extract_s3_key_from_url
from services.logger import configure_logging

log = configure_logging(__name__)


def delete_removed_identity_images(
    template: dict,
    old_template: dict | None,
) -> None:
    """
    Delete S3 objects for identities whose image was removed in the new template.

    Compares identities at the same index in ``template`` and ``old_template``.
    If an identity previously had an image URL but the new version does not,
    the S3 object is deleted.

    Args:
        template: The new template dict containing the updated identities list.
        old_template: The previous template dict. If ``None``, nothing is deleted.
    """
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
                    log.warning(
                        f"Failed to delete removed image at index {index}: {e}"
                    )
