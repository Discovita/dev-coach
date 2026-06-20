from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0006_alter_user_build"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_email_verified",
            field=models.BooleanField(
                default=False,
                help_text="Whether the user has confirmed ownership of their email address.",
            ),
        ),
    ]
