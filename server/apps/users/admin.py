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
    Enhanced admin interface for User model management.

    Features:
    - List view with key user information
    - Filtering by status and roles
    - Search across multiple fields
    - Organized fieldsets for better data management
    - Custom actions for bulk operations
    - Configured for email-based authentication (no username field)
    """

    # Fields shown in the list view
    list_display = (
        "email",
        "get_full_name",
        "is_active",
        "is_admin",
        "is_superuser",
        "is_staff",
        "last_login",
        "date_joined",
    )

    # Fields that can be used to filter the list
    list_filter = (
        "is_active",
        "is_admin",
        "is_superuser",
        "is_staff",
        "date_joined",
        "last_login",
        "email_verification_sent_at",
    )

    # Fields that can be searched
    search_fields = (
        "email",
        "first_name",
        "last_name",
    )

    # Fields that can be edited from the list view
    list_editable = ("is_active",)

    # How many items to show per page
    list_per_page = 25

    # Default ordering
    ordering = ("-date_joined",)

    # Organization of fields in the edit form
    # fieldsets defines the layout of fields when editing an existing user in the admin
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _( "Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_admin",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _( "Email verification"),
            {
                "fields": ("verification_token", "email_verification_sent_at"),
                "classes": ("collapse",),
            },
        ),
        (
            _( "Important dates"),
            {
                "fields": ("last_login", "date_joined", "created_at", "updated_at"),
            },
        ),
    )

    # add_fieldsets defines the layout of fields when creating a new user in the admin
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                # Only email and password fields are required for user creation
                "fields": ("email", "password1", "password2"),
            },
        ),
    )

    # Read-only fields that shouldn't be edited
    readonly_fields = (
        "date_joined",
        "last_login",
        "created_at",
        "updated_at",
        "email_verification_sent_at",
    )

    def get_full_name(self, obj):
        """Get user's full name or email if name not set."""
        return obj.get_full_name() or obj.email

    get_full_name.short_description = _("Full Name")
    get_full_name.admin_order_field = "first_name"  # Allows sorting by this field
