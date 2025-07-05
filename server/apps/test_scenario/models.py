from django.db import models
from django.contrib.auth import get_user_model
import uuid

class TestScenario(models.Model):
    """
    TestScenario
    -------------
    Represents a template-based test scenario for the Discovita Dev Coach.
    Stores a declarative JSON template describing the initial state for all relevant models (User, CoachState, Identity, ChatMessage, UserNote).
    Used for creating, editing, resetting, and managing test user states for comprehensive chatbot testing.
    
    Used by:
      - Scenario management logic in the backend (see docs/Testing_Implementation_Plan.md)
      - Admin UI for test scenario management (list, view, edit, create)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, help_text="Unique name for selecting this test scenario.")
    description = models.TextField(blank=True, help_text="Description for UI display.")
    template = models.JSONField(help_text="Declarative template describing the initial state for all relevant models.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="User who created this scenario (optional)."
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Test Scenario"
        verbose_name_plural = "Test Scenarios"
        ordering = ["-created_at"]

# This model is referenced in docs/Testing_Implementation_Plan.md and is the core of the test scenario system.
