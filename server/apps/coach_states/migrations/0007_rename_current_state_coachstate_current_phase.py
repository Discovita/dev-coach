# Generated by Django 5.1.3 on 2025-05-30 07:13

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "coach_states",
            "0006_coachstate_who_you_are_coachstate_who_you_want_to_be_and_more",
        ),
    ]

    operations = [
        migrations.RenameField(
            model_name="coachstate",
            old_name="current_state",
            new_name="current_phase",
        ),
    ]
