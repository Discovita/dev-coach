# Sentinel User Notes System

## Overview

The **Sentinel User Notes System** is designed to provide long-term, evolving memory for the Discovita Dev Coach chatbot. It automatically extracts and stores important information about users as they interact with the chatbot, enabling the coach to remember key facts and context across sessions. This system is decoupled from the main chat endpoint for performance and maintainability, leveraging Celery for asynchronous processing.

---

## Goals
- **Capture important user information** revealed during chat sessions.
- **Store notes** in a structured, queryable way.
- **Keep the chat endpoint fast** by running note extraction asynchronously.
- **Pass the latest notes** into every new chatbot prompt for richer, more personalized coaching.

---

## Architecture

1. **UserNote Model**: Stores individual notes about a user, extracted from chat messages.
2. **Celery Task**: Runs in the background, processes new user messages, and updates notes using an LLM (the "Sentinel").
3. **Django Signal**: Triggers the Celery task whenever a new user message is saved.
4. **Prompt Integration**: The latest notes are included in the context for every new chatbot prompt.

---

## Implementation Details

### 1. UserNote Model

- Created a new Django model `UserNote` in `server/apps/user_notes/models.py`.
- Each note is associated with a user and may reference the chat message that prompted its creation.
- Uses a UUID as the primary key for uniqueness and future-proofing.
- Includes a timestamp for when the note was created.
- Comprehensive docstrings and comments for maintainability.

```python
import uuid
from django.db import models
from apps.users.models import User
from apps.chat_messages.models import ChatMessage

class UserNote(models.Model):
    """
    Stores a single note about a user, extracted by the Sentinel agent.
    Each note is associated with a user and may reference the chat message that prompted its creation.
    Used by the Sentinel User Notes system to provide long-term memory for the coach.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique identifier for this user note."
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_notes",
        help_text="The user this note belongs to."
    )
    note = models.TextField(
        help_text="A note about the user, extracted from chat."
    )
    source_message = models.ForeignKey(
        ChatMessage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="The chat message that prompted this note, if applicable."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this note was created."
    )

    def __str__(self):
        return f"Note for {self.user.email}: {self.note[:40]}..."
```

---

### 2. Celery Task

- Implemented a Celery task in `server/apps/user_notes/tasks.py` to extract user notes from new chat messages.
- The task fetches the latest user notes and the new message, sends them to the Sentinel LLM, and updates notes as needed.
- Uses the `@shared_task` decorator for easy discovery and integration with Django.
- Keeps the chat endpoint fast by running note extraction asynchronously.

```python
from celery import shared_task
from apps.chat_messages.models import ChatMessage
from services.sentinel.sentinel import Sentinel
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")

@shared_task
def extract_user_notes(chat_message_id):
    user_msg = ChatMessage.objects.get(id=chat_message_id)
    sentinel = Sentinel(user_msg.user)
    sentinel.extract_notes()
```

---

### 3. Django Signal

- Used Django's `post_save` signal on `ChatMessage` to trigger the Celery task **only for user messages**.
- Uses `delay_on_commit()` to ensure the task runs after the DB transaction is committed, avoiding race conditions.
- This decouples the note extraction logic from the main request/response cycle, keeping the app responsive.

```python
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
    """
    if created and instance.role == MessageRole.USER:
        extract_user_notes.delay_on_commit(instance.pk)
```

---

### 4. Sentinel Service

- The `Sentinel` service in `server/services/sentinel/sentinel.py` is responsible for extracting and updating user notes based on chat messages.
- It uses the PromptManager to build a prompt for the LLM, calls the LLM, and applies any actions (such as creating or updating notes) based on the LLM's response.

```python
class Sentinel:
    """
    Service for extracting and updating user notes based on chat messages.
    """
    def __init__(self, user: User):
        self.user = user
        self.prompt_manager = PromptManager()
        self.model = AIModel.GPT_4O_MINI
        try:
            self.coach_state = CoachState.objects.get(user=user)
        except CoachState.DoesNotExist:
            log.error(f"User Coach State Not Found: {user.id}")

    def extract_notes(self):
        ai_service = AIServiceFactory.create(self.model)
        # Use the PromptManager to build the sentinel prompt
        sentinel_prompt, response_format = self.prompt_manager.create_sentinel_prompt(
            self.user, self.model
        )
        log.debug(f"Sentinel LLM prompt:\n{sentinel_prompt}")
        log.debug(f"Sentinel response format: {response_format}")
        response: SentinelChatResponse = ai_service.call_sentinel(
            sentinel_prompt, response_format, self.model
        )
        apply_actions(self.coach_state, response)
        log.debug(f"Sentinel Response: {response}")
```

---

### 5. Including Notes in the Chatbot Prompt

- When building the prompt in your chat endpoint, fetch the latest notes for the user and include them in the context.
- This ensures the coach has access to the most recent and relevant user information for every interaction.

```python
from apps.user_notes.models import UserNote

def get_user_notes_for_prompt(user):
    notes = UserNote.objects.filter(user=user).order_by('-created_at')[:10]
    return [note.note for note in notes]
```

---

## Best Practices
- **Decouple note extraction from the chat endpoint** for performance and maintainability.
- **Use Celery's `delay_on_commit()`** to avoid race conditions.
- **Store each note as a separate record** for flexibility and history.
- **Keep the LLM prompt concise** by limiting the number of notes passed in.
- **Comprehensive comments and docstrings** are included throughout the codebase for future maintainability.

---

## Setup Checklist
1. **Create the `UserNote` model** and run migrations.
2. **Set up Celery** with a broker (e.g., Redis) and configure Django integration.
3. **Implement the Celery task** for note extraction.
4. **Register the Django signal** to trigger the task on new user messages.
5. **Update prompt construction** to include user notes.
6. **Test end-to-end:**
    - Send a user message
    - Confirm the Celery task runs and updates notes
    - Confirm notes are included in subsequent prompts

---

## References
- [Celery Django Integration Docs](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html)
- [Django Signals](https://docs.djangoproject.com/en/stable/topics/signals/)
- [Celery Task Best Practices](https://docs.celeryq.dev/en/stable/userguide/tasks.html)

---

**This system enables the Discovita Dev Coach to remember and leverage important user information, providing a more personalized and effective coaching experience.** 