# Multi-Turn Image Editing Implementation Plan

## Overview

Replace the current single-shot image generation with a chat-based approach using Gemini's multi-turn conversation feature. Users start a new image chat, then iteratively edit the image through conversation.

## Core Concept

```
Start New Chat = Create Gemini chat session → Generate first image → Store chat history
Continue Chat  = Restore chat from history → Send edit message → Update history
```

The Gemini chat maintains context of all previous messages and generated images. We serialize and store the chat history in the database to persist across requests.

---

## Phase 1: Database Model

### New Model: `IdentityImageChat`

Location: `server/apps/users/models/identity_image_chat.py`

This model is added to the `users` app since it's per-user session state.

```python
class IdentityImageChat(Base):
    """
    Persists Gemini chat state for multi-turn identity image editing.
    One chat per user - replaced when starting a new image generation.
    """
    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="identity_image_chat"
    )
    
    identity = models.ForeignKey(
        "identities.Identity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Serialized Gemini chat history - list of Content objects as JSON
    # Images and thought signatures are automatically base64 encoded/decoded
    # by the Google genai SDK's pydantic models
    chat_history = models.JSONField(default=list)
    
    class Meta:
        verbose_name = "Identity Image Chat"
        verbose_name_plural = "Identity Image Chats"
```

### Why This Works

The Google genai SDK's `Content` models use pydantic with:
- `ser_json_bytes='base64'` - bytes (images, thought signatures) serialize to base64
- `val_json_bytes='base64'` - base64 strings deserialize back to bytes

This means we can:
1. Call `chat.get_history(curated=True)` to get `list[Content]`
2. Serialize with `[content.to_json_dict() for content in history]`
3. Store in JSONField
4. Restore with `[Content.model_validate(c) for c in stored_history]`
5. Pass to `client.chats.create(history=restored_history)`

### Files to Update

1. Create `server/apps/users/models/identity_image_chat.py`
2. Update `server/apps/users/models/__init__.py` to export the model
3. Run migrations: `python manage.py makemigrations users`
4. Apply migrations: `python manage.py migrate`
5. (Optional) Add to `server/apps/users/admin.py` for debugging

---

## Phase 2: Service Layer Changes

### GeminiImageService Updates

Location: `server/services/image_generation/gemini_image_service.py`

**New Methods:**

```python
def create_chat(
    self,
    config: Optional[types.GenerateContentConfig] = None
) -> Chat:
    """Create a new Gemini chat session for image generation."""
    return self.client.chats.create(
        model=self.MODEL,
        config=config or types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
        ),
        history=[],
    )

def restore_chat(
    self,
    history: list[dict],
    config: Optional[types.GenerateContentConfig] = None
) -> Chat:
    """Restore a chat session from serialized history."""
    from google.genai.types import Content
    restored_history = [Content.model_validate(c) for c in history]
    return self.client.chats.create(
        model=self.MODEL,
        config=config or types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
        ),
        history=restored_history,
    )

def serialize_chat_history(self, chat: Chat) -> list[dict]:
    """Serialize chat history for database storage."""
    history = chat.get_history(curated=True)
    return [content.to_json_dict() for content in history]

def extract_image_from_response(
    self, 
    response: GenerateContentResponse
) -> Optional[Image.Image]:
    """Extract the generated image from a chat response."""
    for part in response.parts:
        if part.inline_data is not None:
            return part.as_image()
    return None
```

### Orchestration Layer Updates

Location: `server/services/image_generation/orchestration.py`

**New Functions:**

```python
def start_identity_image_chat(
    identity: Identity,
    reference_images: List[ReferenceImage],
    user: User,
    additional_prompt: str = "",
    aspect_ratio: str = "16:9",
    resolution: str = "4K",
) -> tuple[Optional[PILImage.Image], IdentityImageChat]:
    """
    Start a new image generation chat session.
    
    - Creates a new Gemini chat
    - Sends initial prompt with reference images
    - Stores chat history in database (replaces any existing chat for user)
    - Returns generated image and the chat record
    """
    ...

def continue_identity_image_chat(
    user: User,
    edit_prompt: str,
    aspect_ratio: str = "16:9",
    resolution: str = "4K",
) -> tuple[Optional[PILImage.Image], IdentityImageChat]:
    """
    Continue an existing image chat with an edit request.
    
    - Loads existing chat history from database
    - Restores Gemini chat session
    - Sends edit message
    - Updates stored history
    - Returns new image and updated chat record
    
    Raises:
        ValueError: If user has no active chat session
    """
    ...

def get_chat_status(user: User) -> dict:
    """
    Get the status of a user's image chat.
    
    Returns:
        {
            "has_active_chat": bool,
            "identity_id": str | None,
            "identity_name": str | None,
        }
    """
    ...
```

---

## Phase 3: API Endpoints

### Admin Endpoints (for testing with different users)

These endpoints accept a `user_id` parameter to allow admins to test image generation for any user.

#### Start New Chat (Admin)

**`POST /api/v1/admin/identities/start-image-chat/`**

Request:
```json
{
  "identity_id": "uuid",
  "user_id": "uuid",
  "additional_prompt": "string (optional)"
}
```

Response:
```json
{
  "image_base64": "...",
  "identity_id": "uuid",
  "identity_name": "string"
}
```

#### Continue Chat (Admin)

**`POST /api/v1/admin/identities/continue-image-chat/`**

Request:
```json
{
  "user_id": "uuid",
  "edit_prompt": "string"
}
```

Response:
```json
{
  "image_base64": "...",
  "identity_id": "uuid",
  "identity_name": "string"
}
```

---

### User Endpoints (for production)

These endpoints use the authenticated user from the request - no `user_id` parameter needed.

#### Start New Chat (User)

**`POST /api/v1/identities/start-image-chat/`**

Request:
```json
{
  "identity_id": "uuid",
  "additional_prompt": "string (optional)"
}
```

Response:
```json
{
  "image_base64": "...",
  "identity_id": "uuid",
  "identity_name": "string"
}
```

#### Continue Chat (User)

**`POST /api/v1/identities/continue-image-chat/`**

Request:
```json
{
  "edit_prompt": "string"
}
```

Response:
```json
{
  "image_base64": "...",
  "identity_id": "uuid",
  "identity_name": "string"
}
```

---

### Error Responses (Both Admin & User)

| Status | Condition | Message |
|--------|-----------|---------|
| 400 | No active chat | "No active image chat. Please start a new chat first." |
| 400 | Missing edit_prompt | "Edit prompt is required." |
| 400 | Missing identity_id | "Identity ID is required." |
| 400 | No reference images | "Reference images are required for image generation." |
| 404 | User not found (admin) | "User not found." |
| 404 | Identity not found | "Identity not found." |
| 500 | Gemini API failure | "Image generation failed. Please try again." |

---

## Phase 4: Frontend Changes

### Types

Location: `client/src/types/imageGeneration.ts`

```typescript
// Rename/update existing types
interface StartImageChatRequest {
  identity_id: string;
  user_id: string;
  additional_prompt?: string;
}

interface StartImageChatResponse {
  image_base64: string;
  identity_id: string;
  identity_name: string;
}

interface ContinueImageChatRequest {
  user_id: string;
  edit_prompt: string;
}

interface ContinueImageChatResponse {
  image_base64: string;
  identity_id: string;
  identity_name: string;
}
```

### API Layer

Location: `client/src/api/imageGeneration.ts`

```typescript
export async function startImageChat(
  request: StartImageChatRequest
): Promise<StartImageChatResponse> {
  // POST to /admin/identities/start-image-chat/
}

export async function continueImageChat(
  request: ContinueImageChatRequest
): Promise<ContinueImageChatResponse> {
  // POST to /admin/identities/continue-image-chat/
}
```

### Hook Updates

Location: `client/src/hooks/use-image-generation.ts`

- Rename `generateImage` → `startChat`
- Add `continueChat` mutation
- Add `isContinuing` state
- Track chat status from responses

### UI Updates

Location: `client/src/pages/images/Images.tsx`

After successful generation, show edit section:

```
┌─────────────────────────────────────────┐
│  [Generated Image Display]              │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │ Edit this image:                │    │
│  │ [Text input for edit prompt   ] │    │
│  │                                 │    │
│  │ [Apply Edit]  [Start New]       │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

**Behavior:**
- "Apply Edit" → Calls continue-chat endpoint, updates displayed image
- "Start New" → Calls start-chat endpoint (replaces chat), updates displayed image
- Both buttons disabled while loading

---

## Phase 5: Error Handling

### Backend

| Scenario | Response | Message |
|----------|----------|---------|
| Continue with no chat | 400 | "No active image chat. Please start a new chat first." |
| Continue with empty prompt | 400 | "Edit prompt is required." |
| User not found | 404 | "User not found." |
| Gemini API failure | 500 | "Image generation failed. Please try again." |
| Reference images missing | 400 | "Reference images are required for image generation." |

### Frontend

- Display error messages in toast notifications (using sonner)
- Disable edit UI if no active chat
- Clear edit input after successful edit
- Show "No active chat" state gracefully

---

## Implementation Order

### Step 1: Database Model
- [ ] Create `server/apps/users/models/identity_image_chat.py`
- [ ] Update `server/apps/users/models/__init__.py` to export the model
- [ ] Run migrations: `python manage.py makemigrations users`
- [ ] Apply migrations: `python manage.py migrate`
- [ ] (Optional) Add to `server/apps/users/admin.py` for debugging

### Step 2: Service Layer
- [ ] Add chat methods to `GeminiImageService` (create, restore, serialize, extract)
- [ ] Add `start_identity_image_chat()` to orchestration
- [ ] Add `continue_identity_image_chat()` to orchestration
- [ ] Add `get_chat_status()` helper

### Step 3: API Endpoints
- [ ] Add admin `start-image-chat` endpoint (accepts user_id)
- [ ] Add admin `continue-image-chat` endpoint (accepts user_id)
- [ ] Add user `start-image-chat` endpoint (uses authenticated user)
- [ ] Add user `continue-image-chat` endpoint (uses authenticated user)
- [ ] Add proper error responses for all endpoints
- [ ] (Optional) Deprecate old `generate-image` endpoint

### Step 4: Frontend - Types & API
- [ ] Update types for new request/response shapes
- [ ] Add `startImageChat` API function
- [ ] Add `continueImageChat` API function

### Step 5: Frontend - Hook & UI
- [ ] Update `useImageGeneration` hook with new methods
- [ ] Update Images page UI with edit flow
- [ ] Wire up start/continue chat flows

### Step 6: Testing
- [ ] Test start → continue → continue flow
- [ ] Test start → start (chat replacement)
- [ ] Test error cases (no chat, empty prompt)
- [ ] Test with different users (admin feature)
- [ ] Verify chat history serialization/deserialization

---

## Key Technical Details

### Chat History Contains Everything

The serialized chat history includes:
- User messages (prompts)
- Model responses (text + generated images)
- Thought signatures (for model reasoning continuity)

Images are base64 encoded in the `inline_data` field. The SDK handles encoding/decoding automatically.

### No Need to Pass Previous Image

When continuing a chat, we DON'T need to explicitly pass the previous image. The restored chat history contains all context, including previously generated images. Gemini uses this context to understand edit requests.

### Reference Images

Reference images are sent with the initial prompt when starting a new chat. For edits, we may want to include them again if they're relevant to the edit request.

---

## Questions Resolved

- **Model name**: `IdentityImageChat` (specific to purpose)
- **Session scope**: Per-user, replaced on "Start New"
- **What we store**: Serialized chat history (includes images + thought signatures)
- **Image in history**: Yes, automatically - no separate storage needed
- **Reference images**: Sent with initial chat; optional on continue
- **Storage location**: `users` app (per-user session state)
- **Endpoints**: Both admin (with user_id) and user (authenticated) endpoints built together
