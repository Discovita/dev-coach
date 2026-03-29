"""
TestScenario model definition.

See: apps/test_scenario/models/__init__.py
"""

import uuid

from django.contrib.auth import get_user_model
from django.db import models


class TestScenario(models.Model):
    """
    Template-based test scenario for the Discovita Dev Coach.

    Stores a declarative JSON template describing the initial state for all
    relevant models (User, CoachState, Identity, ChatMessage, UserNote, Action).
    Used for creating, resetting, and managing test user states for
    comprehensive chatbot testing.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Unique name for selecting this test scenario.",
    )
    description = models.TextField(blank=True, help_text="Description for UI display.")
    template = models.JSONField(
        help_text="Declarative template describing the initial state for all relevant models."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="User who created this scenario (optional).",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Test Scenario"
        verbose_name_plural = "Test Scenarios"
        ordering = ["-created_at"]
