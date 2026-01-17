"""
Management command to seed the image generation prompt into the database.
Creates the initial version of the prompt if it doesn't exist.
"""

from django.core.management.base import BaseCommand
from apps.prompts.models import Prompt
from enums.prompt_type import PromptType
from enums.context_keys import ContextKey


IMAGE_GENERATION_PROMPT_BODY = """We're creating an Identity Image for this person.

{identity_context}

{appearance_context}

{scene_context}

Create a professional, confident, and inspiring image for this Identity.
It is critical that the person's face remains intact and recognizable.
The image should be an ideal visualization of them living as this Identity.
Give it a movie poster quality aesthetic.
Nothing negative should be conveyed - this is an aspirational image.

Additional instructions: {additional_prompt}
"""


class Command(BaseCommand):
    help = "Seed the image generation prompt into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force create a new version even if one exists",
        )

    def handle(self, *args, **options):
        force = options["force"]

        # Check if an image generation prompt already exists
        existing = Prompt.objects.filter(
            prompt_type=PromptType.IMAGE_GENERATION,
            is_active=True,
        ).order_by("-version").first()

        if existing and not force:
            self.stdout.write(
                self.style.WARNING(
                    f"Image generation prompt already exists (version {existing.version}). "
                    "Use --force to create a new version."
                )
            )
            return

        # Determine version number
        if existing:
            version = existing.version + 1
            # Deactivate old version
            existing.is_active = False
            existing.save()
            self.stdout.write(f"Deactivated version {existing.version}")
        else:
            version = 1

        # Create the prompt
        prompt = Prompt.objects.create(
            coaching_phase=None,  # Not tied to a coaching phase
            version=version,
            name="Identity Image Generation Prompt",
            description="Prompt template for generating identity images using Gemini. "
                        "Uses {identity_context}, {appearance_context}, {scene_context}, and {additional_prompt} placeholders.",
            body=IMAGE_GENERATION_PROMPT_BODY,
            required_context_keys=[ContextKey.IDENTITY_FOR_IMAGE],
            allowed_actions=[],  # No actions for image generation
            prompt_type=PromptType.IMAGE_GENERATION,
            is_active=True,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created image generation prompt version {prompt.version} (id: {prompt.id})"
            )
        )

