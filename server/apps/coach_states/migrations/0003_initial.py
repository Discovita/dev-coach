# Generated by Django 5.1.5 on 2025-05-11 10:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("coach_states", "0002_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="coachstate",
            name="user",
            field=models.OneToOneField(
                help_text="The user this coach state belongs to.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="coach_state",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
