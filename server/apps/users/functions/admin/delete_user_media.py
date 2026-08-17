"""
delete_user_media

Remove a user's generated and uploaded files from storage. Used by
``delete_user_account`` so deleting a user does not strand their objects
in S3 — nothing else references them once the rows are gone.
"""

from django.core.files.storage import default_storage

from apps.users.models import User
from services.logger import configure_logging

log = configure_logging(__name__)


def collect_user_media_keys(user: User) -> list[str]:
    """
    Gather every storage key belonging to ``user``.

    Two shapes are involved. Meditation files are recorded as bare S3 key
    strings (``MeditationAsset.s3_key``, ``Meditation.final_video_s3_key``),
    including every generated version, not just the active one. Identity and
    reference images are ``VersatileImageField`` files, whose ``name`` is the
    storage key.

    Must be called before the user is deleted — afterwards the rows are gone.

    Args:
        user: The user whose media should be collected.

    Returns:
        Storage keys, deduplicated, with empty values dropped.
    """
    from apps.identities.models import Identity
    from apps.meditations.models import Meditation, MeditationAsset
    from apps.reference_images.models import ReferenceImage

    keys: list[str] = []

    keys.extend(
        MeditationAsset.objects.filter(segment__meditation__user=user)
        .exclude(s3_key="")
        .values_list("s3_key", flat=True)
    )
    keys.extend(
        Meditation.objects.filter(user=user)
        .exclude(final_video_s3_key="")
        .values_list("final_video_s3_key", flat=True)
    )

    for model in (Identity, ReferenceImage):
        for instance in model.objects.filter(user=user).exclude(image=""):
            if not instance.image:
                continue
            # Sized renditions live alongside the original under their own
            # prefix and are not covered by deleting the original's key.
            try:
                instance.image.delete_all_created_images()
            except Exception as e:
                log.warning(f"Failed to delete image renditions: {e}")
            keys.append(instance.image.name)

    return list(dict.fromkeys(key for key in keys if key))


def delete_media_keys(keys: list[str]) -> None:
    """
    Delete storage objects by key, one failure at a time.

    A storage error is logged and skipped rather than raised: the database
    rows are already gone by this point, so aborting would leave the caller
    with a half-finished delete it cannot retry. The cost of a failure is an
    orphaned file, which is what this function exists to reduce, not a
    broken reference.

    Args:
        keys: Storage keys to remove.
    """
    for key in keys:
        try:
            default_storage.delete(key)
        except Exception as e:
            log.warning(f"Failed to delete media object {key}: {e}")
