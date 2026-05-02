"""
Admin configuration for the Prompt model.

See: apps/prompts/admin/__init__.py
"""

from django.contrib import admin

from apps.prompts.models import Prompt


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for viewing and managing Prompt records.

    Provides search, filtering, and ordering capabilities for
    prompt management.
    """

    list_display = (
        "id",
        "coaching_phase",
        "version",
        "name",
        "prompt_type",
        "is_active",
        "created_at",
        "updated_at",
    )
    search_fields = ("id", "coaching_phase", "name", "description", "body")
    list_filter = ("coaching_phase", "is_active", "created_at", "updated_at")
    ordering = ("-created_at",)
