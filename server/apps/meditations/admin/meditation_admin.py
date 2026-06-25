"""
Admin for the meditation models. Read-mostly: lets an admin inspect
meditations, their segments, and the versioned assets.
"""

from django.contrib import admin

from apps.meditations.models import Meditation, MeditationAsset, MeditationSegment


class MeditationSegmentInline(admin.TabularInline):
    model = MeditationSegment
    extra = 0
    fields = ("order", "identity", "created_at")
    readonly_fields = ("created_at",)
    raw_id_fields = ("identity",)
    show_change_link = True


class MeditationAssetInline(admin.TabularInline):
    model = MeditationAsset
    extra = 0
    fields = ("kind", "version", "status", "is_active", "s3_key", "error_code")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Meditation)
class MeditationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "created_at", "updated_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__email", "user__first_name", "user__last_name")
    readonly_fields = ("id", "created_at", "updated_at")
    raw_id_fields = ("user",)
    inlines = (MeditationSegmentInline,)


@admin.register(MeditationSegment)
class MeditationSegmentAdmin(admin.ModelAdmin):
    list_display = ("id", "meditation", "identity", "order", "created_at")
    list_filter = ("created_at",)
    search_fields = ("meditation__user__email", "identity__name")
    readonly_fields = ("id", "created_at", "updated_at")
    raw_id_fields = ("meditation", "identity")
    inlines = (MeditationAssetInline,)


@admin.register(MeditationAsset)
class MeditationAssetAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "segment",
        "kind",
        "version",
        "status",
        "is_active",
        "created_at",
    )
    list_filter = ("kind", "status", "is_active", "created_at")
    search_fields = ("segment__meditation__user__email",)
    readonly_fields = ("id", "created_at", "updated_at")
    raw_id_fields = ("segment",)
