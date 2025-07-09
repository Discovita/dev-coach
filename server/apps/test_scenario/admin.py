from django.contrib import admin
from .models import TestScenario

@admin.register(TestScenario)
class TestScenarioAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_by", "created_at", "updated_at", "id")
    search_fields = ("name", "description", "created_by__email")
    list_filter = ("created_by", "created_at")
    ordering = ("-created_at",)
