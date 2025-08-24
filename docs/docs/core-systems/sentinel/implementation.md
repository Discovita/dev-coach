# Implementation

## Implementation Details

### 1. UserNote Model

The `UserNote` model was created specifically for the Sentinel Memory System to store extracted user information. For detailed information about the model structure, see the [UserNote database model documentation](../../database/models/user-note).

| Field            | Type          | Description                                                   |
| ---------------- | ------------- | ------------------------------------------------------------- |
| `id`             | UUID          | Primary key, auto-generated unique identifier                 |
| `user`           | ForeignKey    | Reference to the User this note belongs to                    |
| `note`           | TextField     | The extracted note content about the user                     |
| `source_message` | ForeignKey    | Optional reference to the ChatMessage that prompted this note |
| `created_at`     | DateTimeField | Timestamp when the note was created                           |

### 2. Celery Task

```python
from celery import shared_task
from apps.chat_messages.models import ChatMessage
from services.sentinel.sentinel import Sentinel
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")

@shared_task
def extract_user_notes(chat_message_id):
    """
    Celery task to extract user notes from a new chat message.
    Runs asynchronously to keep the chat endpoint fast.
    """
    user_msg = ChatMessage.objects.get(id=chat_message_id)
    sentinel = Sentinel(user_msg.user)
    sentinel.extract_notes()
```

### 3. Django Signal

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

### 4. Sentinel Service

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
        """
        Extract user notes from the latest chat message.
        Uses the PromptManager to build the sentinel prompt and calls the AI service.
        """
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

### 5. Prompt Manager Integration

The Prompt Manager automatically includes user notes in every coaching prompt. In the `create_chat_prompt` method, user notes are prepended to the prompt:

```python
def create_chat_prompt(self, user: User, model: AIModel, version_override: int = None) -> str:
    # ... existing prompt assembly code ...

    # Prepend any current user notes
    coach_prompt = prepend_user_notes(coach_prompt, coach_state)

    # ... rest of prompt assembly ...
```

This ensures that the extracted user information from the Sentinel system is automatically included in every coaching interaction, providing the AI with the user's background and context.
