import uuid
from django.db import models
# from enums.context_key import ContextKey
from django.contrib.postgres.fields import ArrayField
from apps.users.models import User


class Prompt(models.Model):
    id = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False,
    unique=True,
    help_text="Unique identifier for this object."
)
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prompts",
    )
    prompt_key = models.CharField(
        max_length=255, help_text="Logical group for all versions of a prompt"
    )
    version = models.IntegerField(default=1, help_text="Version number of the prompt")
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    body = models.TextField(help_text="Prompt body")
    # required_context_keys = ArrayField(
    #     models.CharField(max_length=64, choices=ContextKey.choices),
    #     default=list,
    #     help_text="List of required context keys for this prompt",
    # )
    is_active = models.BooleanField(default=True, help_text="Is this prompt active?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("prompt_key", "version")
