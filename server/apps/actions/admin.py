from django.contrib import admin
from .models import Action


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    """
    Admin interface for the Action model.
    Provides a view into all actions taken by the coach system.
    """
    
    list_display = [
        'action_type', 
        'user', 
        'timestamp', 
        'result_summary',
        'test_scenario',
        'coach_message_preview'
    ]
    
    list_filter = [
        'action_type',
        'timestamp',
        'test_scenario',
        'user',
    ]
    
    search_fields = [
        'user__username',
        'user__email',
        'action_type',
        'parameters',
    ]
    
    readonly_fields = [
        'id',
        'timestamp',
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'action_type', 'timestamp')
        }),
        ('Action Details', {
            'fields': ('parameters', 'result_summary', 'coach_message')
        }),
        ('Test Scenario', {
            'fields': ('test_scenario',),
            'classes': ('collapse',)
        }),
    )
    
    def coach_message_preview(self, obj):
        """
        Show a preview of the coach message content.
        """
        if obj.coach_message:
            content = obj.coach_message.content
            return content[:50] + "..." if len(content) > 50 else content
        return "No message"
    
    coach_message_preview.short_description = "Coach Message Preview"
    
    def has_add_permission(self, request):
        """
        Actions should only be created by the system, not manually.
        """
        return False
    
    def has_change_permission(self, request, obj=None):
        """
        Actions should not be modified after creation.
        """
        return False
