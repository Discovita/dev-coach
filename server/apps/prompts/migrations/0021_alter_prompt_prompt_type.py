"""
Add the VIDEO_GENERATION choice to Prompt.prompt_type (choices-only change).
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("prompts", "0020_seed_video_generation_prompt"),
    ]

    operations = [
        migrations.AlterField(
            model_name="prompt",
            name="prompt_type",
            field=models.CharField(
                choices=[
                    ("coach", "Coach"),
                    ("sentinel", "Sentinel"),
                    ("system", "System"),
                    ("image_generation", "Image Generation"),
                    ("video_generation", "Video Generation"),
                ],
                default="coach",
                help_text="Type of prompt (coach, sentinel, system, etc.)",
                max_length=32,
            ),
        ),
    ]
