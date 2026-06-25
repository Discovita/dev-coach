"""
set_active_asset — make one asset the active version for its (segment, kind).

Demotes the currently-active sibling and promotes the target in a single
transaction so the "at most one active per (segment, kind)" constraint is never
violated.
"""

from django.db import transaction

from apps.meditations.models import MeditationAsset


def set_active_asset(asset: MeditationAsset) -> MeditationAsset:
    """Promote *asset* to active, demoting any other active asset of the same
    (segment, kind)."""
    with transaction.atomic():
        MeditationAsset.objects.filter(
            segment_id=asset.segment_id, kind=asset.kind, is_active=True
        ).exclude(pk=asset.pk).update(is_active=False)
        if not asset.is_active:
            asset.is_active = True
            asset.save(update_fields=["is_active", "updated_at"])
    return asset
