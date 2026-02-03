# Multi-Turn Image Editing - Backend Implementation Plan

This document provides the detailed backend implementation plan following the project's coding standards.

---

## File Structure Overview

After implementation, the affected directories will look like this:

```
server/
├── apps/
│   └── identities/
│       ├── models/
│       │   ├── __init__.py                    # Add export for IdentityImageChat
│       │   ├── identity.py                    # Existing
│       │   └── identity_image_chat.py         # NEW: Chat session model
│       ├── functions/                         # NEW directory
│       │   ├── __init__.py
│       │   ├── admin/
│       │   │   ├── __init__.py
│       │   │   ├── admin_start_image_chat.py  # NEW
│       │   │   └── admin_continue_image_chat.py # NEW
│       │   └── public/
│       │       ├── __init__.py
│       │       ├── start_image_chat.py        # NEW
│       │       └── continue_image_chat.py     # NEW
│       ├── serializers/                       # Convert from single file to directory
│       │   ├── __init__.py
│       │   ├── identity_serializer.py         # MOVE existing serializer here
│       │   ├── start_image_chat_request.py    # NEW
│       │   ├── continue_image_chat_request.py # NEW
│       │   └── image_chat_response.py         # NEW
│       ├── tests/                             # NEW directory (or add to existing)
│       │   ├── __init__.py
│       │   ├── test_identity_image_chat_model.py # NEW
│       │   ├── test_start_image_chat.py       # NEW
│       │   └── test_continue_image_chat.py    # NEW
│       └── views/
│           ├── __init__.py                    # Add exports for new ViewSets
│           ├── admin_identity_view_set.py     # Existing (no changes)
│           ├── admin_identity_image_chat_view_set.py # NEW: Admin chat endpoints
│           ├── identity_view_set.py           # Existing (no changes)
│           └── identity_image_chat_view_set.py # NEW: User-facing chat endpoints
│
├── services/
│   └── image_generation/
│       ├── __init__.py
│       ├── gemini_image_service.py            # MODIFY: Add chat methods
│       ├── orchestration.py                   # MODIFY: Add chat orchestration
│       └── utils/
│           ├── __init__.py                    # Add export
│           └── chat_history_serializer.py     # NEW: Serialize/deserialize chat history
│
└── apps/api_urls.py                           # MODIFY: Register new viewsets
```

**Key Organization Principle:**
- Everything for this feature lives in `identities` - model, functions, serializers, views, tests
- Both admin and public get their own ViewSets (consistent separation of concerns)
- The model has a FK to User but lives in identities because it's identity-image-specific functionality

---

## Phase 1: Database Model

### File: `server/apps/identities/models/identity_image_chat.py`

```python
"""
IdentityImageChat Model

Persists Gemini chat state for multi-turn identity image editing.
One chat per user - replaced when starting a new image generation.

The chat_history field stores serialized Gemini Content objects as JSON.
Images and thought signatures are automatically base64 encoded/decoded
by the Google genai SDK's pydantic models.
"""

from django.db import models

from apps.core.models import Base


class IdentityImageChat(Base):
    """
    Persists Gemini chat state for multi-turn identity image editing.

    One chat per user - replaced when starting a new image generation.
    The chat history contains all messages, generated images, and thought
    signatures needed to continue the conversation.

    Related to:
    - apps.users.models.User (OneToOne via user field)
    - apps.identities.models.Identity (FK via identity field)
    """

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------

    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="identity_image_chat",
        help_text="The user this chat session belongs to. One chat per user.",
    )

    identity = models.ForeignKey(
        "identities.Identity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="image_chats",
        help_text="The identity this chat is generating images for.",
    )

    # -------------------------------------------------------------------------
    # Chat State
    # -------------------------------------------------------------------------

    chat_history = models.JSONField(
        default=list,
        help_text="Serialized Gemini chat history (list of Content objects as JSON). "
        "Includes messages, generated images (base64), and thought signatures.",
    )

    class Meta:
        verbose_name = "Identity Image Chat"
        verbose_name_plural = "Identity Image Chats"

    def __str__(self) -> str:
        identity_name = self.identity.name if self.identity else "No identity"
        return f"ImageChat for {self.user.email} - {identity_name}"
```

### File: `server/apps/identities/models/__init__.py`

Update exports:

```python
from .identity import Identity
from .identity_image_chat import IdentityImageChat

__all__ = ["Identity", "IdentityImageChat"]
```

### Migration Command

```bash
cd server && source .venv/bin/activate && python manage.py makemigrations identities
cd server && source .venv/bin/activate && python manage.py migrate
```

---

## Phase 2: Service Layer

### File: `server/services/image_generation/utils/chat_history_serializer.py`

```python
"""
Chat History Serialization Utilities

Functions for serializing and deserializing Gemini chat history
to/from JSON for database storage.
"""

from typing import List

from google.genai.types import Content

from services.logger import configure_logging

log = configure_logging(__name__)


def serialize_chat_history(history: List[Content]) -> List[dict]:
    """
    Serialize Gemini chat history for database storage.

    The Google genai SDK's Content model uses pydantic with:
    - ser_json_bytes='base64': bytes (images, thought signatures) become base64 strings
    - val_json_bytes='base64': base64 strings become bytes on load

    Args:
        history: List of Content objects from chat.get_history()

    Returns:
        List of JSON-serializable dicts
    """
    return [content.to_json_dict() for content in history]


def deserialize_chat_history(history_data: List[dict]) -> List[Content]:
    """
    Deserialize stored chat history back to Content objects.

    Args:
        history_data: List of dicts from database JSONField

    Returns:
        List of Content objects for restoring a chat session
    """
    return [Content.model_validate(item) for item in history_data]
```

### File: `server/services/image_generation/utils/__init__.py`

Add exports:

```python
from .load_pil_images import load_pil_images_from_references
from .chat_history_serializer import serialize_chat_history, deserialize_chat_history

__all__ = [
    "load_pil_images_from_references",
    "serialize_chat_history",
    "deserialize_chat_history",
]
```

### File: `server/services/image_generation/gemini_image_service.py`

Add these methods to the `GeminiImageService` class:

```python
# New imports at top
from typing import List, Optional, Tuple
from google.genai.chats import Chat
from google.genai.types import Content, GenerateContentConfig, GenerateContentResponse


# Add these methods to GeminiImageService class:

def create_chat(
    self,
    history: Optional[List[Content]] = None,
    config: Optional[GenerateContentConfig] = None,
) -> Chat:
    """
    Create a new Gemini chat session for image generation.

    Args:
        history: Optional existing history to restore a session
        config: Optional config override

    Returns:
        Gemini Chat object
    """
    default_config = GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(
            aspect_ratio="16:9",
            image_size="4K",
        ),
    )

    return self.client.chats.create(
        model=self.MODEL,
        config=config or default_config,
        history=history or [],
    )


def send_chat_message(
    self,
    chat: Chat,
    message: str,
    images: Optional[List[Image.Image]] = None,
) -> Tuple[Optional[Image.Image], GenerateContentResponse]:
    """
    Send a message to a chat session and extract the generated image.

    Args:
        chat: The Gemini chat session
        message: Text message/prompt to send
        images: Optional PIL images to include with the message

    Returns:
        Tuple of (generated PIL Image or None, full response)
    """
    # Build content: text + optional images
    contents = [message]
    if images:
        contents.extend(images)

    log.info(f"Sending chat message with {len(images) if images else 0} images")
    log.debug(f"Message: {message[:200]}...")

    response = chat.send_message(contents)

    # Extract image from response
    generated_image = None
    for part in response.parts:
        if part.inline_data is not None:
            generated_image = part.as_image()
            log.info("Image generated successfully from chat")
            break
        if part.text is not None:
            log.debug(f"Chat response text: {part.text[:200]}...")

    return generated_image, response
```

### File: `server/services/image_generation/orchestration.py`

Replace/extend with new orchestration functions:

```python
"""
Identity Image Generation Orchestration.

This module provides high-level orchestration functions for:
- Starting new image generation chat sessions
- Continuing existing chat sessions with edit prompts

Used by:
- AdminIdentityViewSet (admin endpoints)
- IdentityImageChatViewSet (user endpoints)
"""

from PIL import Image as PILImage
from typing import List, Optional, Tuple

from apps.identities.models import Identity, IdentityImageChat
from apps.reference_images.models import ReferenceImage
from apps.users.models import User
from services.image_generation.gemini_image_service import GeminiImageService
from services.image_generation.utils import (
    load_pil_images_from_references,
    serialize_chat_history,
    deserialize_chat_history,
)
from services.prompt_manager.manager import PromptManager
from services.logger import configure_logging

log = configure_logging(__name__)


def start_identity_image_chat(
    identity: Identity,
    reference_images: List[ReferenceImage],
    user: User,
    additional_prompt: str = "",
) -> Tuple[Optional[PILImage.Image], IdentityImageChat]:
    """
    Start a new image generation chat session.

    Creates a new Gemini chat, sends the initial prompt with reference images,
    stores the chat history in the database (replacing any existing chat),
    and returns the generated image.

    Args:
        identity: The Identity to generate an image for
        reference_images: List of ReferenceImage models for the user
        user: The User for appearance preferences and context
        additional_prompt: Optional extra instructions

    Returns:
        Tuple of (generated PIL Image or None, IdentityImageChat record)

    Raises:
        ValueError: If no reference images could be loaded
    """
    log.info(f"Starting new image chat for identity: {identity.name}, user: {user.id}")

    # 1. Build the initial prompt
    prompt_manager = PromptManager()
    prompt = prompt_manager.create_image_generation_prompt(
        identity=identity,
        user=user,
        additional_prompt=additional_prompt,
    )
    log.debug(f"Built prompt: {prompt[:100]}...")

    # 2. Load PIL images from references
    pil_images = load_pil_images_from_references(reference_images)
    log.info(f"Loaded {len(pil_images)} reference images")

    if not pil_images:
        raise ValueError("No reference images could be loaded")

    # 3. Create new Gemini chat and send initial message
    service = GeminiImageService()
    chat = service.create_chat()

    generated_image, response = service.send_chat_message(
        chat=chat,
        message=prompt,
        images=pil_images,
    )

    # 4. Serialize and store chat history
    history = chat.get_history(curated=True)
    serialized_history = serialize_chat_history(history)

    # 5. Create or replace the user's chat session
    chat_record, created = IdentityImageChat.objects.update_or_create(
        user=user,
        defaults={
            "identity": identity,
            "chat_history": serialized_history,
        },
    )

    action = "Created" if created else "Replaced"
    log.info(f"{action} chat session for user {user.id}, identity {identity.name}")

    return generated_image, chat_record


def continue_identity_image_chat(
    user: User,
    edit_prompt: str,
    reference_images: Optional[List[ReferenceImage]] = None,
) -> Tuple[Optional[PILImage.Image], IdentityImageChat]:
    """
    Continue an existing image chat with an edit request.

    Loads the existing chat history, restores the Gemini chat session,
    sends the edit prompt, updates the stored history, and returns the new image.

    Args:
        user: The User whose chat to continue
        edit_prompt: The edit instruction (e.g., "make the lighting warmer")
        reference_images: Optional reference images to include with the edit

    Returns:
        Tuple of (generated PIL Image or None, updated IdentityImageChat record)

    Raises:
        ValueError: If user has no active chat session
    """
    log.info(f"Continuing image chat for user: {user.id}")

    # 1. Load existing chat session
    try:
        chat_record = IdentityImageChat.objects.get(user=user)
    except IdentityImageChat.DoesNotExist:
        raise ValueError("No active image chat. Please start a new chat first.")

    if not chat_record.chat_history:
        raise ValueError("Chat history is empty. Please start a new chat first.")

    # 2. Deserialize history and restore chat
    history = deserialize_chat_history(chat_record.chat_history)

    service = GeminiImageService()
    chat = service.create_chat(history=history)

    # 3. Optionally load reference images
    pil_images = None
    if reference_images:
        pil_images = load_pil_images_from_references(reference_images)
        log.info(f"Including {len(pil_images)} reference images with edit")

    # 4. Send edit message
    generated_image, response = service.send_chat_message(
        chat=chat,
        message=edit_prompt,
        images=pil_images,
    )

    # 5. Update stored history
    updated_history = chat.get_history(curated=True)
    chat_record.chat_history = serialize_chat_history(updated_history)
    chat_record.save()

    log.info(f"Updated chat session for user {user.id}")

    return generated_image, chat_record


# Keep existing function for backwards compatibility (can deprecate later)
def generate_identity_image(
    identity: Identity,
    reference_images: List[ReferenceImage],
    user: User,
    additional_prompt: str = "",
    aspect_ratio: str = "16:9",
    resolution: str = "4K",
) -> Optional[PILImage.Image]:
    """
    DEPRECATED: Use start_identity_image_chat instead.

    Generate an identity image using Gemini (single-shot, no session).
    Kept for backwards compatibility during transition.
    """
    # ... existing implementation ...
```

---

## Phase 3: Serializers

**Note:** The identities app currently has a single `serializer.py` file. We need to convert it to a `serializers/` directory following the one-file-per-serializer standard.

### Step 3a: Convert to Directory Structure

1. Create `server/apps/identities/serializers/` directory
2. Move existing `serializer.py` content to `serializers/identity_serializer.py`
3. Delete original `serializer.py`
4. Create `serializers/__init__.py` with exports

### File: `server/apps/identities/serializers/identity_serializer.py`

Move existing `IdentitySerializer` content here (from current `serializer.py`).

### File: `server/apps/identities/serializers/start_image_chat_request.py`

```python
"""
StartImageChatRequest Serializer

Validates request data for starting a new image chat session.
"""

from rest_framework import serializers


class StartImageChatRequestSerializer(serializers.Serializer):
    """
    Validates request data for the start-image-chat endpoint.

    For admin endpoints, user_id is required.
    For user endpoints, user_id is not included (uses authenticated user).
    """

    identity_id = serializers.UUIDField(
        help_text="UUID of the identity to generate an image for"
    )

    user_id = serializers.UUIDField(
        required=False,
        help_text="UUID of the user (admin only - omit for user endpoints)"
    )

    additional_prompt = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Optional additional instructions for image generation"
    )
```

### File: `server/apps/identities/serializers/continue_image_chat_request.py`

```python
"""
ContinueImageChatRequest Serializer

Validates request data for continuing an image chat session.
"""

from rest_framework import serializers


class ContinueImageChatRequestSerializer(serializers.Serializer):
    """
    Validates request data for the continue-image-chat endpoint.

    For admin endpoints, user_id is required.
    For user endpoints, user_id is not included (uses authenticated user).
    """

    user_id = serializers.UUIDField(
        required=False,
        help_text="UUID of the user (admin only - omit for user endpoints)"
    )

    edit_prompt = serializers.CharField(
        help_text="The edit instruction (e.g., 'make the lighting warmer')"
    )

    def validate_edit_prompt(self, value: str) -> str:
        """Ensure edit prompt is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Edit prompt is required.")
        return value.strip()
```

### File: `server/apps/identities/serializers/image_chat_response.py`

```python
"""
ImageChatResponse Serializer

Documents the response shape for image chat endpoints.
"""

from rest_framework import serializers


class ImageChatResponseSerializer(serializers.Serializer):
    """
    Response format for start-image-chat and continue-image-chat endpoints.
    """

    image_base64 = serializers.CharField(
        help_text="Base64 encoded PNG image"
    )

    identity_id = serializers.UUIDField(
        help_text="UUID of the identity the image was generated for"
    )

    identity_name = serializers.CharField(
        help_text="Name of the identity"
    )
```

### File: `server/apps/identities/serializers/__init__.py`

```python
"""
Identity Serializers

Data serialization for identity-related API requests and responses.
"""

from .identity_serializer import IdentitySerializer
from .start_image_chat_request import StartImageChatRequestSerializer
from .continue_image_chat_request import ContinueImageChatRequestSerializer
from .image_chat_response import ImageChatResponseSerializer

__all__ = [
    "IdentitySerializer",
    "StartImageChatRequestSerializer",
    "ContinueImageChatRequestSerializer",
    "ImageChatResponseSerializer",
]
```

---

## Phase 4: Functions

**Note:** The identities app doesn't have a `functions/` directory yet. We need to create it following the standard structure.

### Directory Setup

Create the following structure:
```
server/apps/identities/functions/
├── __init__.py
├── admin/
│   ├── __init__.py
│   ├── admin_start_image_chat.py
│   └── admin_continue_image_chat.py
└── public/
    ├── __init__.py
    ├── start_image_chat.py
    └── continue_image_chat.py
```

### File: `server/apps/identities/functions/admin/admin_start_image_chat.py`

```python
"""
Start Image Chat (Admin)

Admin function to start a new image generation chat session for any user.
"""

import base64
import tempfile
import os

from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

from apps.identities.models import Identity
from apps.reference_images.models import ReferenceImage
from services.image_generation.orchestration import start_identity_image_chat
from services.logger import configure_logging

log = configure_logging(__name__)

User = get_user_model()


def admin_start_image_chat(
    identity_id: str,
    user_id: str,
    additional_prompt: str = "",
) -> Response:
    """
    Start a new image generation chat for a specified user (admin only).

    Creates a new Gemini chat session, generates the initial image,
    and stores the chat history for future edits.

    Args:
        identity_id: UUID of the identity to generate for
        user_id: UUID of the target user
        additional_prompt: Optional extra instructions

    Returns:
        Response with image_base64, identity_id, identity_name

    Raises:
        DRF exceptions for validation errors (400, 404, 500)
    """
    from rest_framework.exceptions import NotFound, ValidationError

    # Validate identity exists
    try:
        identity = Identity.objects.get(id=identity_id)
    except Identity.DoesNotExist:
        raise NotFound(f"Identity {identity_id} not found")

    # Validate user exists
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise NotFound(f"User {user_id} not found")

    # Get reference images
    reference_images = list(ReferenceImage.objects.filter(user_id=user_id))
    if not reference_images:
        raise ValidationError(
            f"No reference images found for user {user_id}. "
            "Reference images are required for image generation."
        )

    # Start the chat session
    try:
        pil_image, chat_record = start_identity_image_chat(
            identity=identity,
            reference_images=reference_images,
            user=target_user,
            additional_prompt=additional_prompt,
        )
    except ValueError as e:
        raise ValidationError(str(e))
    except Exception as e:
        log.error(f"Image generation failed: {e}", exc_info=True)
        from rest_framework.exceptions import APIException

        raise APIException(f"Image generation failed: {str(e)}")

    if not pil_image:
        from rest_framework.exceptions import APIException

        raise APIException("Image generation failed - no image was generated")

    # Convert PIL image to base64
    image_base64 = _pil_to_base64(pil_image)

    return Response(
        {
            "image_base64": image_base64,
            "identity_id": str(identity.id),
            "identity_name": identity.name,
        },
        status=status.HTTP_200_OK,
    )


def _pil_to_base64(pil_image) -> str:
    """Convert a PIL/Gemini image to base64 string."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        tmp_path = tmp_file.name

    try:
        pil_image.save(tmp_path)
        with open(tmp_path, "rb") as f:
            image_bytes = f.read()
        return base64.b64encode(image_bytes).decode("utf-8")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
```

### File: `server/apps/identities/functions/admin/admin_continue_image_chat.py`

```python
"""
Continue Image Chat (Admin)

Admin function to continue an image chat session for any user.
"""

import base64
import tempfile
import os

from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

from apps.reference_images.models import ReferenceImage
from services.image_generation.orchestration import continue_identity_image_chat
from services.logger import configure_logging

log = configure_logging(__name__)

User = get_user_model()


def admin_continue_image_chat(
    user_id: str,
    edit_prompt: str,
) -> Response:
    """
    Continue an existing image chat for a specified user (admin only).

    Loads the user's existing chat session, sends the edit prompt,
    and returns the new generated image.

    Args:
        user_id: UUID of the target user
        edit_prompt: The edit instruction

    Returns:
        Response with image_base64, identity_id, identity_name

    Raises:
        DRF exceptions for validation errors (400, 404, 500)
    """
    from rest_framework.exceptions import NotFound, ValidationError, APIException

    # Validate user exists
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise NotFound(f"User {user_id} not found")

    # Optionally get reference images (include with edit if available)
    reference_images = list(ReferenceImage.objects.filter(user_id=user_id))

    # Continue the chat session
    try:
        pil_image, chat_record = continue_identity_image_chat(
            user=target_user,
            edit_prompt=edit_prompt,
            reference_images=reference_images if reference_images else None,
        )
    except ValueError as e:
        raise ValidationError(str(e))
    except Exception as e:
        log.error(f"Image edit failed: {e}", exc_info=True)
        raise APIException(f"Image edit failed: {str(e)}")

    if not pil_image:
        raise APIException("Image edit failed - no image was generated")

    # Convert PIL image to base64
    image_base64 = _pil_to_base64(pil_image)

    identity = chat_record.identity

    return Response(
        {
            "image_base64": image_base64,
            "identity_id": str(identity.id) if identity else None,
            "identity_name": identity.name if identity else None,
        },
        status=status.HTTP_200_OK,
    )


def _pil_to_base64(pil_image) -> str:
    """Convert a PIL/Gemini image to base64 string."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        tmp_path = tmp_file.name

    try:
        pil_image.save(tmp_path)
        with open(tmp_path, "rb") as f:
            image_bytes = f.read()
        return base64.b64encode(image_bytes).decode("utf-8")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
```

### File: `server/apps/identities/functions/admin/__init__.py`

```python
"""
Admin Functions for Identities

Admin-only business logic functions for identity image generation.
"""

from .admin_start_image_chat import admin_start_image_chat
from .admin_continue_image_chat import admin_continue_image_chat

__all__ = [
    "admin_start_image_chat",
    "admin_continue_image_chat",
]
```

### File: `server/apps/identities/functions/public/start_image_chat.py`

Similar to admin version but uses `request.user` instead of `user_id` parameter.

### File: `server/apps/identities/functions/public/continue_image_chat.py`

Similar to admin version but uses `request.user` instead of `user_id` parameter.

### File: `server/apps/identities/functions/public/__init__.py`

```python
"""
Public Functions for Identities

User-facing business logic functions for identity image generation.
"""

from .start_image_chat import start_image_chat
from .continue_image_chat import continue_image_chat

__all__ = [
    "start_image_chat",
    "continue_image_chat",
]
```

### File: `server/apps/identities/functions/__init__.py`

```python
"""
Identity Functions

Business logic functions for identity operations.
"""

from .admin import admin_start_image_chat, admin_continue_image_chat
from .public import start_image_chat, continue_image_chat

__all__ = [
    "admin_start_image_chat",
    "admin_continue_image_chat",
    "start_image_chat",
    "continue_image_chat",
]
```

---

## Phase 5: ViewSets

### File: `server/apps/identities/views/admin_identity_image_chat_view_set.py` (NEW)

```python
"""
Admin Identity Image Chat ViewSet

Admin endpoints for image generation chat sessions.
Allows admins to test image chat for any user.
"""

from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request

from apps.identities.serializers import (
    StartImageChatRequestSerializer,
    ContinueImageChatRequestSerializer,
)
from apps.identities.functions.admin import (
    admin_start_image_chat,
    admin_continue_image_chat,
)
from services.logger import configure_logging

log = configure_logging(__name__)


class AdminIdentityImageChatViewSet(viewsets.GenericViewSet):
    """
    Admin endpoints for identity image generation chat.

    Endpoints:
    - POST /api/v1/admin/identity-image-chat/start/   → start_chat()
    - POST /api/v1/admin/identity-image-chat/continue/ → continue_chat()
    """

    permission_classes = [IsAdminUser]

    @action(
        detail=False,
        methods=["POST"],
        url_path="start",
    )
    def start_chat(self, request: Request) -> Response:
        """
        Start a new image generation chat session.

        POST /api/v1/admin/identity-image-chat/start/

        Creates a new Gemini chat session for the specified user,
        replacing any existing session.

        Body (JSON):
            - identity_id: UUID of the identity (required)
            - user_id: UUID of the user (required)
            - additional_prompt: Extra instructions (optional)

        Returns: 200 OK with image_base64, identity_id, identity_name
        """
        serializer = StartImageChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return admin_start_image_chat(
            identity_id=str(serializer.validated_data["identity_id"]),
            user_id=str(serializer.validated_data["user_id"]),
            additional_prompt=serializer.validated_data.get("additional_prompt", ""),
        )

    @action(
        detail=False,
        methods=["POST"],
        url_path="continue",
    )
    def continue_chat(self, request: Request) -> Response:
        """
        Continue an existing image chat with an edit prompt.

        POST /api/v1/admin/identity-image-chat/continue/

        Loads the user's existing chat session and sends an edit request.

        Body (JSON):
            - user_id: UUID of the user (required)
            - edit_prompt: Edit instruction (required)

        Returns: 200 OK with image_base64, identity_id, identity_name
        Errors:
            - 400: No active chat, empty edit prompt
            - 404: User not found
            - 500: Image generation failed
        """
        serializer = ContinueImageChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return admin_continue_image_chat(
            user_id=str(serializer.validated_data["user_id"]),
            edit_prompt=serializer.validated_data["edit_prompt"],
        )
```

### File: `server/apps/identities/views/identity_image_chat_view_set.py` (NEW)

```python
"""
Identity Image Chat ViewSet

User-facing endpoints for image generation chat sessions.
Uses the authenticated user - no user_id parameter needed.
"""

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.request import Request

from apps.identities.serializers import (
    StartImageChatRequestSerializer,
    ContinueImageChatRequestSerializer,
)
from apps.identities.functions.public import (
    start_image_chat,
    continue_image_chat,
)
from services.logger import configure_logging

log = configure_logging(__name__)


class IdentityImageChatViewSet(viewsets.GenericViewSet):
    """
    User-facing endpoints for identity image generation.

    Endpoints:
    - POST /api/v1/identity-image-chat/start/   → start_chat()
    - POST /api/v1/identity-image-chat/continue/ → continue_chat()
    """

    permission_classes = [IsAuthenticated]

    @action(
        detail=False,
        methods=["POST"],
        url_path="start",
    )
    def start_chat(self, request: Request) -> Response:
        """
        Start a new image generation chat session.

        POST /api/v1/identity-image-chat/start/

        Creates a new Gemini chat session for the authenticated user,
        replacing any existing session.

        Body (JSON):
            - identity_id: UUID of the identity (required)
            - additional_prompt: Extra instructions (optional)

        Returns: 200 OK with image_base64, identity_id, identity_name
        """
        serializer = StartImageChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return start_image_chat(
            user=request.user,
            identity_id=str(serializer.validated_data["identity_id"]),
            additional_prompt=serializer.validated_data.get("additional_prompt", ""),
        )

    @action(
        detail=False,
        methods=["POST"],
        url_path="continue",
    )
    def continue_chat(self, request: Request) -> Response:
        """
        Continue an existing image chat with an edit prompt.

        POST /api/v1/identity-image-chat/continue/

        Loads the authenticated user's existing chat session
        and sends an edit request.

        Body (JSON):
            - edit_prompt: Edit instruction (required)

        Returns: 200 OK with image_base64, identity_id, identity_name
        Errors:
            - 400: No active chat, empty edit prompt
            - 500: Image generation failed
        """
        serializer = ContinueImageChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return continue_image_chat(
            user=request.user,
            edit_prompt=serializer.validated_data["edit_prompt"],
        )
```

### File: `server/apps/identities/views/__init__.py`

Update exports:

```python
from .identity_view_set import IdentityViewSet
from .admin_identity_view_set import AdminIdentityViewSet
from .admin_identity_image_chat_view_set import AdminIdentityImageChatViewSet
from .identity_image_chat_view_set import IdentityImageChatViewSet

__all__ = [
    "IdentityViewSet",
    "AdminIdentityViewSet",
    "AdminIdentityImageChatViewSet",
    "IdentityImageChatViewSet",
]
```

---

## Phase 6: URL Registration

### File: `server/apps/api_urls.py`

Add imports and registrations:

```python
# Add to imports:
from apps.identities.views import (
    AdminIdentityImageChatViewSet,
    IdentityImageChatViewSet,
)

# Add to admin_router registrations:
admin_router.register(
    r"identity-image-chat",
    AdminIdentityImageChatViewSet,
    basename="admin-identity-image-chat"
)

# Add to default_router registrations:
default_router.register(
    r"identity-image-chat",
    IdentityImageChatViewSet,
    basename="identity-image-chat"
)
```

This gives clean URL paths:
- Admin: `/api/v1/admin/identity-image-chat/start/` and `/api/v1/admin/identity-image-chat/continue/`
- Public: `/api/v1/identity-image-chat/start/` and `/api/v1/identity-image-chat/continue/`

---

## Phase 7: Tests

### Test Files to Create

```
server/apps/identities/tests/
├── test_identity_image_chat_model.py   # Model tests
├── test_start_image_chat.py            # Function/endpoint tests
└── test_continue_image_chat.py
```

### Tests to Write

#### `test_identity_image_chat_model.py`

| Test Name | What It Tests |
|-----------|---------------|
| `test_create_chat_record` | Can create a chat record for a user |
| `test_one_to_one_constraint` | Only one chat per user (update_or_create works) |
| `test_identity_nullable` | Identity FK can be null |
| `test_cascade_delete_with_user` | Chat deleted when user deleted |
| `test_chat_history_default_empty` | chat_history defaults to empty list |
| `test_str_representation` | __str__ returns expected format |

#### `test_start_image_chat.py`

| Test Name | What It Tests |
|-----------|---------------|
| `test_start_chat_success` | Successfully starts chat and returns image |
| `test_start_chat_creates_record` | Creates IdentityImageChat record |
| `test_start_chat_replaces_existing` | Starting new chat replaces existing |
| `test_start_chat_missing_identity` | Returns 404 for missing identity |
| `test_start_chat_missing_user` | Returns 404 for missing user (admin) |
| `test_start_chat_no_reference_images` | Returns 400 if no reference images |
| `test_start_chat_requires_auth` | Returns 401 without authentication |
| `test_admin_start_chat_requires_admin` | Admin endpoint requires admin user |

#### `test_continue_image_chat.py`

| Test Name | What It Tests |
|-----------|---------------|
| `test_continue_chat_success` | Successfully continues chat and returns image |
| `test_continue_chat_updates_history` | Chat history is updated after edit |
| `test_continue_chat_no_session` | Returns 400 if no existing session |
| `test_continue_chat_empty_prompt` | Returns 400 for empty edit prompt |
| `test_continue_chat_missing_user` | Returns 404 for missing user (admin) |
| `test_continue_chat_requires_auth` | Returns 401 without authentication |
| `test_admin_continue_chat_requires_admin` | Admin endpoint requires admin user |

#### Service Layer Tests

| Test Name | What It Tests |
|-----------|---------------|
| `test_serialize_chat_history` | Serializes Content objects to JSON |
| `test_deserialize_chat_history` | Deserializes JSON back to Content objects |
| `test_serialization_round_trip` | Serialize → Deserialize preserves data |

---

## Implementation Order Checklist

### Step 1: Model & Migration (identities app)
- [ ] Create `server/apps/identities/models/identity_image_chat.py`
- [ ] Update `server/apps/identities/models/__init__.py`
- [ ] Run `python manage.py makemigrations identities`
- [ ] Run `python manage.py migrate`

### Step 2: Service Layer Utilities
- [ ] Create `server/services/image_generation/utils/chat_history_serializer.py`
- [ ] Update `server/services/image_generation/utils/__init__.py`

### Step 3: Gemini Service Methods
- [ ] Add `create_chat()` to `GeminiImageService`
- [ ] Add `send_chat_message()` to `GeminiImageService`

### Step 4: Orchestration Functions
- [ ] Add `start_identity_image_chat()` to orchestration.py
- [ ] Add `continue_identity_image_chat()` to orchestration.py

### Step 5: Serializers (identities app)
- [ ] Convert `serializer.py` to `serializers/` directory
- [ ] Move existing serializer to `serializers/identity_serializer.py`
- [ ] Create `serializers/start_image_chat_request.py`
- [ ] Create `serializers/continue_image_chat_request.py`
- [ ] Create `serializers/image_chat_response.py`
- [ ] Create `serializers/__init__.py` with all exports
- [ ] Update imports in views that use IdentitySerializer

### Step 6: Functions - Admin (identities app)
- [ ] Create `functions/` directory structure
- [ ] Create `functions/admin/admin_start_image_chat.py`
- [ ] Create `functions/admin/admin_continue_image_chat.py`
- [ ] Create `functions/admin/__init__.py`

### Step 7: Functions - Public (identities app)
- [ ] Create `functions/public/start_image_chat.py`
- [ ] Create `functions/public/continue_image_chat.py`
- [ ] Create `functions/public/__init__.py`
- [ ] Create `functions/__init__.py`

### Step 8: ViewSets
- [ ] Create `AdminIdentityImageChatViewSet`
- [ ] Create `IdentityImageChatViewSet`
- [ ] Update `views/__init__.py`

### Step 9: URL Registration
- [ ] Register `AdminIdentityImageChatViewSet` in admin_router
- [ ] Register `IdentityImageChatViewSet` in default_router

### Step 10: Tests
- [ ] Write model tests in `apps/identities/tests/test_identity_image_chat_model.py`
- [ ] Write function/endpoint tests in `apps/identities/tests/test_start_image_chat.py`
- [ ] Write function/endpoint tests in `apps/identities/tests/test_continue_image_chat.py`
- [ ] Run all tests

---

## API Summary

### Admin Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/api/v1/admin/identity-image-chat/start/` | Start new chat (requires user_id) |
| POST | `/api/v1/admin/identity-image-chat/continue/` | Continue chat (requires user_id) |

### User Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/api/v1/identity-image-chat/start/` | Start new chat (uses auth user) |
| POST | `/api/v1/identity-image-chat/continue/` | Continue chat (uses auth user) |

### Request/Response Formats

**Start Image Chat Request (Admin):**
```json
{
  "identity_id": "uuid",
  "user_id": "uuid",
  "additional_prompt": "optional string"
}
```

**Start Image Chat Request (User):**
```json
{
  "identity_id": "uuid",
  "additional_prompt": "optional string"
}
```

**Continue Image Chat Request (Admin):**
```json
{
  "user_id": "uuid",
  "edit_prompt": "make the lighting warmer"
}
```

**Continue Image Chat Request (User):**
```json
{
  "edit_prompt": "make the lighting warmer"
}
```

**Response (both endpoints):**
```json
{
  "image_base64": "base64-encoded-png",
  "identity_id": "uuid",
  "identity_name": "The Artist"
}
```
