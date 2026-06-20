"""
Admin registration for the User model.

Provides a rich admin interface with email-based authentication,
comprehensive filtering, appearance-preference fieldsets, and
inline reference images.

See: apps/users/admin/__init__.py
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from apps.reference_images.admin import ReferenceImageInline
from apps.users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for the custom User model."""

    inlines = [ReferenceImageInline]

    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_email_verified",
        "is_staff",
        "is_active",
        "is_superuser",
        "created_at",
        "test_scenario_display",
    )
    list_filter = (
        "is_email_verified",
        "is_staff",
        "is_active",
        "is_superuser",
        "test_scenario",
    )
    actions = ("mark_email_verified", "mark_email_unverified")
    search_fields = ("email", "first_name", "last_name", "test_scenario__name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
        (
            "Verification",
            {
                "fields": (
                    "is_email_verified",
                    "verification_token",
                    "email_verification_sent_at",
                )
            },
        ),
        (
            "Appearance Preferences",
            {
                "fields": (
                    "gender",
                    "skin_tone",
                    "hair_color",
                    "eye_color",
                    "height",
                    "build",
                    "age_range",
                ),
                "description": "User appearance preferences for image generation visualization.",
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "is_superuser",
                ),
            },
        ),
    )
    ordering = ("email",)
    readonly_fields = (
        "created_at",
        "updated_at",
        "last_login",
        "email_verification_sent_at",
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_full_name(self, obj):
        """Return user's full name, falling back to email."""
        return obj.get_full_name() or obj.email

    get_full_name.short_description = _("Full Name")
    get_full_name.admin_order_field = "first_name"

    def test_scenario_display(self, obj):
        """Display the name of the associated test scenario, if any."""
        return obj.test_scenario.name if obj.test_scenario else None

    test_scenario_display.short_description = "Test Scenario"
    test_scenario_display.admin_order_field = "test_scenario__name"

    @admin.action(description="Mark selected users as email verified")
    def mark_email_verified(self, request, queryset):
        """Bulk-mark the selected users' email addresses as verified."""
        updated = queryset.update(is_email_verified=True)
        self.message_user(request, f"Marked {updated} user(s) as email verified.")

    @admin.action(description="Mark selected users as email NOT verified")
    def mark_email_unverified(self, request, queryset):
        """Bulk-mark the selected users' email addresses as not verified."""
        updated = queryset.update(is_email_verified=False)
        self.message_user(request, f"Marked {updated} user(s) as email not verified.")
