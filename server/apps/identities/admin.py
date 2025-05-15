from django.contrib import admin
from .models import Identity


@admin.register(Identity)
class IdentityAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Identity model.
    """

    list_display = (
        "id",
        "user",
        "name",
        "affirmation",
        "visualization",
        "state",
        "notes",
        "category",
        "created_at",
        "updated_at",
    )
    list_filter = ("state", "category", "created_at")
    search_fields = ("user__email",)
    readonly_fields = ("created_at", "updated_at")
