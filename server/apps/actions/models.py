import uuid
from django.db import models
from enums.action_type import ActionType
from apps.users.models import User
from apps.chat_messages.models import ChatMessage


class Action(models.Model):
    """
    Tracks actions taken by the coach during conversations.
    Each action is linked to the specific coach message that triggered it.
    
    Used in: Coach action tracking, conversation reconstruction, debugging
    Referenced in: Coach views, action handler, admin interface
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique identifier for this action."
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="actions",
        help_text="The user this action belongs to.",
        db_index=True,
    )
    
    action_type = models.CharField(
        max_length=64,
        choices=ActionType.choices,
        help_text="Type of action performed by the coach."
    )
    
    parameters = models.JSONField(
        help_text="Parameters passed to the action (stored as JSON)."
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the action was performed.",
        db_index=True,
    )
    
    # Link to the coach message that triggered this action
    coach_message = models.ForeignKey(
        ChatMessage,
        on_delete=models.CASCADE,
        related_name="triggered_actions",
        help_text="The coach message that triggered this action."
    )
    
    test_scenario = models.ForeignKey(
        'test_scenario.TestScenario',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Test scenario this action is associated with (for test data isolation)."
    )

    class Meta:
        verbose_name = "Action"
        verbose_name_plural = "Actions"
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['coach_message']),
            models.Index(fields=['action_type']),
        ]

    def __str__(self):
        """
        String representation of the action for admin/debugging.
        """
        return f"{self.action_type} - {self.user.username} - {self.timestamp}"
