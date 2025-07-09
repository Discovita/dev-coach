"""
Django Signal: Trigger Sentinel User Notes Extraction on New User Message

This module uses Django's signal framework to watch for new ChatMessage objects.
When a new message is created with role USER, it triggers a Celery task to extract/update user notes.

How it works:
- Django's post_save signal is emitted after a model's save() method completes.
- We connect a receiver function to ChatMessage's post_save signal.
- If the new message is from a USER, we schedule the extract_user_notes Celery task.
- We use delay_on_commit to ensure the task runs only after the database transaction is committed (avoids race conditions).

This decouples the note extraction logic from the main request/response cycle, keeping the app responsive.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.chat_messages.models import ChatMessage
from enums.message_role import MessageRole
from apps.user_notes.tasks import extract_user_notes
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


@receiver(post_save, sender=ChatMessage)
def trigger_sentinel_on_user_message(sender, instance, created, **kwargs):
    """
    Signal receiver for ChatMessage post_save.
    If a new ChatMessage is created and its role is USER, trigger the Celery task to extract user notes.
    Uses delay_on_commit to ensure the task runs after the DB transaction is committed.
    Skips extraction if the message is associated with a test scenario (test data isolation).
    """
    if created and instance.role == MessageRole.USER:
        # Do not extract notes for test scenario messages
        if instance.test_scenario_id is not None:
            log.debug(f"Skipping user note extraction for test scenario message: {instance.id}")
            return
        extract_user_notes.delay_on_commit(instance.pk)
