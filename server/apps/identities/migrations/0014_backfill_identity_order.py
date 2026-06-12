"""
Backfill the new Identity.order field.

For each user, assign order = 0, 1, 2, ... to their identities sorted by
created_at ascending (then id, for stable ordering of same-timestamp rows).
This makes the default ordering "earliest created first" explicit and gives
the reorder feature a sensible starting point.
"""

from django.db import migrations


def backfill_order(apps, schema_editor):
    Identity = apps.get_model("identities", "Identity")

    user_ids = (
        Identity.objects.order_by("user_id")
        .values_list("user_id", flat=True)
        .distinct()
    )

    for user_id in user_ids:
        identities = Identity.objects.filter(user_id=user_id).order_by(
            "created_at", "id"
        )
        to_update = []
        for index, identity in enumerate(identities):
            if identity.order != index:
                identity.order = index
                to_update.append(identity)
        if to_update:
            Identity.objects.bulk_update(to_update, ["order"])


def noop_reverse(apps, schema_editor):
    # Order values are harmless to leave in place on reverse.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("identities", "0013_alter_identity_options_identity_order"),
    ]

    operations = [
        migrations.RunPython(backfill_order, noop_reverse),
    ]
