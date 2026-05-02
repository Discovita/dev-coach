# Generated manually for Action.updated_at

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("actions", "0007_alter_action_action_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="action",
            name="updated_at",
            field=models.DateTimeField(
                auto_now=True,
                db_index=True,
                default=django.utils.timezone.now,
                help_text="When this row was last updated (e.g. summary tweaks).",
            ),
            preserve_default=False,
        ),
    ]
