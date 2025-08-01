# Generated by Django 5.1.3 on 2025-07-05 07:31

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("prompts", "0009_prompt_prompt_type_alter_prompt_allowed_actions_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="prompt",
            name="allowed_actions",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    choices=[
                        ("create_identity", "Create Identity"),
                        ("update_identity", "Update Identity"),
                        ("accept_identity", "Accept Identity"),
                        ("accept_identity_refinement", "Accept Identity Refinement"),
                        ("add_identity_note", "Add Identity Note"),
                        ("transition_phase", "Transition Phase"),
                        ("select_identity_focus", "Select Identity Focus"),
                        ("skip_identity_category", "Skip Identity Category"),
                        ("unskip_identity_category", "Unskip Identity Category"),
                        ("update_who_you_are", "Update Who You Are"),
                        ("update_who_you_want_to_be", "Update Who You Want to Be"),
                        ("add_user_note", "Add User Note"),
                        ("update_user_note", "Update User Note"),
                        ("delete_user_note", "Delete User Note"),
                    ],
                    max_length=64,
                ),
                blank=True,
                default=list,
                help_text="List of allowed action types for this prompt.",
                size=None,
            ),
        ),
        migrations.AlterField(
            model_name="prompt",
            name="coaching_phase",
            field=models.CharField(
                blank=True,
                choices=[
                    ("system_context", "System Context"),
                    ("introduction", "Introduction"),
                    ("get_to_know_you", "Get to Know You"),
                    ("identity_warm_up", "Identity Warm-Up"),
                    ("identity_brainstorming", "Identity Brainstorming"),
                    ("identity_refinement", "Identity Refinement"),
                ],
                help_text="The phase of the coach this prompt is associated with.",
                max_length=32,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="prompt",
            name="required_context_keys",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    choices=[
                        ("user_name", "User Name"),
                        ("identities", "Identities"),
                        ("number_of_identities", "Number of Identities"),
                        ("identity_focus", "Identity Focus"),
                        ("who_you_are", "Who You Are"),
                        ("who_you_want_to_be", "Who You Want to Be"),
                        ("focused_identities", "Focused Identities"),
                        ("user_notes", "User Notes"),
                        ("current_message", "Current Message"),
                        ("previous_message", "Previous Message"),
                        ("current_phase", "Current Phase"),
                        (
                            "brainstorming_category_context",
                            "Brainstorming Category Context",
                        ),
                    ],
                    max_length=64,
                ),
                blank=True,
                default=list,
                help_text="List of required context keys for this prompt.",
                size=None,
            ),
        ),
    ]
