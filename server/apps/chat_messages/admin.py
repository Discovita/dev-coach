from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """
    Admin configuration for the ChatMessage model.
    """
    list_display = ("id", "user", "role", "content", "timestamp")
    list_filter = ("role", "timestamp")
    search_fields = ("content", "user__email")
    readonly_fields = ("timestamp",)
