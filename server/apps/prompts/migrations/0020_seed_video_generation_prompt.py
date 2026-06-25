"""
Seed an initial active VIDEO_GENERATION prompt.

The meditations feature builds a per-segment video prompt by formatting the
latest active VIDEO_GENERATION prompt with identity + scene context. This
migration seeds version 1 so the feature works on a fresh database; the wording
can be refined later via the prompts admin (a new version supersedes this one).
"""

from django.db import migrations

VIDEO_GENERATION_PROMPT_BODY = """\
You are generating a short, cinematic motion video clip for a personal \
meditation. The clip gently animates a still portrait of a person embodying a \
specific identity.

Keep the motion subtle, calm, and serene: soft natural breathing, a slow, \
steady camera push-in, gentle ambient light. The subject's appearance, \
clothing, and setting must stay consistent with the reference image (the first \
frame). No abrupt movements, no scene changes, no text or captions.

IDENTITY:
{identity_context}

SCENE:
{scene_context}

ADDITIONAL DIRECTION:
{additional_prompt}
"""


def seed_prompt(apps, schema_editor):
    Prompt = apps.get_model("prompts", "Prompt")
    Prompt.objects.get_or_create(
        prompt_type="video_generation",
        coaching_phase=None,
        version=1,
        defaults={
            "name": "Video Generation v1",
            "description": "Initial meditations video-generation prompt (Veo).",
            "body": VIDEO_GENERATION_PROMPT_BODY,
            "is_active": True,
        },
    )


def unseed_prompt(apps, schema_editor):
    Prompt = apps.get_model("prompts", "Prompt")
    Prompt.objects.filter(
        prompt_type="video_generation", coaching_phase=None, version=1
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("prompts", "0019_alter_prompt_unique_together"),
    ]

    operations = [
        migrations.RunPython(seed_prompt, unseed_prompt),
    ]
