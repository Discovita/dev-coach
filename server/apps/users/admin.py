"""
Admin configuration for users app.

This module provides a rich admin interface for managing User models with:
- Comprehensive list display
- Filtering capabilities
- Search functionality
- Field organization
- Custom actions
- Email-based authentication (login with email, not username)
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin configuration for the custom User model.
    """
    # Fields to display in the admin list view
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active", "is_superuser", "created_at")
    # Fields to filter by in the admin list view
    list_filter = ("is_staff", "is_active", "is_superuser")
    # Fields to search by
    search_fields = ("email", "first_name", "last_name")
    # Fieldsets for the detail/edit view
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
        ("Verification", {"fields": ("verification_token", "email_verification_sent_at")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_staff", "is_active", "is_superuser"),
        }),
    )
    ordering = ("email",)
    readonly_fields = ("created_at", "updated_at", "last_login", "email_verification_sent_at")

    # Use email as the unique identifier
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_full_name(self, obj):
        """Get user's full name or email if name not set."""
        return obj.get_full_name() or obj.email

    get_full_name.short_description = _("Full Name")
    get_full_name.admin_order_field = "first_name"  # Allows sorting by this field
