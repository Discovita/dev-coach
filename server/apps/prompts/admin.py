from django.contrib import admin
from .models import Prompt


# Custom admin for the Prompt model
class PromptAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Prompt model.
    Shows key fields in the list display, enables search and filtering.
    Used for managing prompts in the Django admin panel.
    """

    list_display = (
        "id",
        "coach_state",
        "version",
        "name",
        "is_active",
        "created_at",
        "updated_at",
    )
    search_fields = ("id", "coach_state", "name", "description", "body")
    list_filter = ("coach_state", "is_active", "created_at", "updated_at")
    ordering = ("-created_at",)


# Register the Prompt model with the custom admin
admin.site.register(Prompt, PromptAdmin)
