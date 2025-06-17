# Sentinel User Notes System

## Overview

The **Sentinel User Notes System** adds long-term, evolving memory to the Discovita Dev Coach chatbot. It automatically extracts and stores important information about users as they interact with the chatbot, enabling the coach to remember key facts and context across sessions.

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

```python
# apps/user_notes/models.py
import uuid
from django.db import models
from apps.users.models import User
from apps.chat_messages.models import ChatMessage

class UserNote(models.Model):
    """
    Stores a single note about a user, extracted by the Sentinel agent.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_notes")
    note = models.TextField(help_text="A note about the user, extracted from chat.")
    source_message = models.ForeignKey(ChatMessage, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note for {self.user.email}: {self.note[:40]}..."
```

---

### 2. Celery Task

- The task fetches the latest user notes and the new message, sends them to the Sentinel LLM, and updates notes as needed.
- Use the `@shared_task` decorator for easy discovery.

```python
# apps/user_notes/tasks.py
from celery import shared_task
from apps.user_notes.models import UserNote
from apps.chat_messages.models import ChatMessage
from apps.users.models import User

@shared_task(ignore_result=True)
def extract_user_notes(chat_message_id):
    message = ChatMessage.objects.get(pk=chat_message_id)
    user = message.user
    # Fetch latest notes for the user
    notes = list(UserNote.objects.filter(user=user).order_by('-created_at'))
    # Call your LLM here (pseudo-code):
    # new_notes = sentinel_llm(notes, message.content)
    # For each new note, create a UserNote if it's not a duplicate
    # ...
    pass  # Implement LLM call and note creation logic
```

---

### 3. Django Signal

- Use `post_save` on `ChatMessage` to trigger the Celery task **only for user messages**.
- Use `delay_on_commit()` to ensure the task runs after the DB transaction is committed.

```python
# apps/chat_messages/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.chat_messages.models import ChatMessage
from enums.message_role import MessageRole
from apps.user_notes.tasks import extract_user_notes

@receiver(post_save, sender=ChatMessage)
def trigger_sentinel_on_user_message(sender, instance, created, **kwargs):
    if created and instance.role == MessageRole.USER:
        extract_user_notes.delay_on_commit(instance.pk)
```

---

### 4. Including Notes in the Chatbot Prompt

- When building the prompt in your chat endpoint, fetch the latest notes for the user and include them in the context.

```python
# Example (in your prompt manager or view)
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