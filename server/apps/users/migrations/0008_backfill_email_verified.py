from django.db import migrations


def mark_existing_verified(apps, schema_editor):
    """
    Grandfather every pre-existing account as email-verified.

    Login is now gated on ``is_email_verified``. Accounts created before that
    gate existed were never asked to verify, so mark them verified to avoid
    locking them out. Only brand-new sign-ups (created after this migration)
    start unverified and must confirm their email.
    """
    User = apps.get_model("users", "User")
    User.objects.filter(is_email_verified=False).update(is_email_verified=True)


def noop_reverse(apps, schema_editor):
    """No-op: we cannot know which users were backfilled vs. genuinely verified."""


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0007_user_is_email_verified"),
    ]

    operations = [
        migrations.RunPython(mark_existing_verified, noop_reverse),
    ]
