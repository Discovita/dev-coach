from django.contrib import admin

from apps.identities.models import IdentityImageChat


@admin.register(IdentityImageChat)
class IdentityImageChatAdmin(admin.ModelAdmin):
    """
    Admin configuration for the IdentityImageChat model.
    """

    list_display = (
        "id",
        "user",
        "identity",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at", "updated_at")
    search_fields = ("user__email", "identity__name")
    readonly_fields = ("created_at", "updated_at", "chat_history_preview")

    def chat_history_preview(self, obj):
        """Display a preview of the chat history."""
        if obj.chat_history:
            return f"{len(obj.chat_history)} messages"
        return "No history"

    chat_history_preview.short_description = "Chat History"
