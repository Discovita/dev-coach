# Multi-Turn Image Editing Implementation Plan

## Overview

Replace the current single-shot image generation with a session-based approach that allows iterative editing. Users generate an image, then make small tweaks without starting from scratch.

## Core Concept

```
Generate New = Create session + Generate first image
Edit Image = Load session + Pass previous image + Edit prompt → New image
```

Sessions are stored in the database, attached to users. Each user has one active session at a time.

---

## Phase 1: Database Model

### New Model: `ImageGenerationSession`

Location: `server/apps/image_generation/models.py` (new app) or add to existing app

```python
class ImageGenerationSession(Base):
    """
    Stores the current image generation session for a user.
    One session per user - replaced when starting fresh.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="image_generation_session"
    )
    
    # The most recently generated image (base64 encoded)
    # Used as input for edit operations
    current_image_base64 = models.TextField(blank=True, null=True)
    
    # The identity this session is generating for
    identity = models.ForeignKey(
        Identity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # The prompt used to generate the current image
    # Useful for debugging and potentially for context
    last_prompt = models.TextField(blank=True)
    
    # Track when reference images were last updated
    # If references change, we might want to indicate this to user
    reference_images_hash = models.CharField(max_length=64, blank=True)
    
    class Meta:
        verbose_name = "Image Generation Session"
        verbose_name_plural = "Image Generation Sessions"
```

### Migration

- Create new model
- One-to-one relationship with User ensures one session per user

---

## Phase 2: Service Layer Changes

### GeminiImageService Updates

Location: `server/services/image_generation/gemini_image_service.py`

**Changes:**
1. Keep existing `generate_image()` method (low-level, just calls Gemini)
2. Add `edit_image()` method that accepts previous image + edit prompt

```python
def edit_image(
    self,
    edit_prompt: str,
    previous_image: Image.Image,
    reference_images: List[Image.Image],
    aspect_ratio: str = "16:9",
    resolution: str = "4K",
) -> Optional[Image.Image]:
    """
    Edit an existing image using Gemini.
    
    Passes the previous image along with reference images and edit prompt.
    Gemini understands this as an edit request.
    """
    # Contents: edit_prompt + previous_image + reference_images
    contents = [edit_prompt, previous_image] + reference_images
    
    # Same generate_content call, but with previous image included
    ...
```

### Orchestration Layer Updates

Location: `server/services/image_generation/orchestration.py`

**New/Modified Functions:**

1. `start_image_session(identity, reference_images, user, additional_prompt, ...)` 
   - Creates/replaces ImageGenerationSession for user
   - Generates initial image
   - Stores image in session
   - Returns image

2. `edit_image_session(user, edit_prompt, reference_images)`
   - Loads existing session for user
   - Validates session exists and has image
   - Calls `edit_image()` with previous image
   - Updates session with new image
   - Returns image

3. `get_session_status(user)` (optional helper)
   - Returns whether user has active session
   - Used by frontend to show/hide edit UI

---

## Phase 3: API Endpoints

### Modify Existing Endpoint

**`POST /api/v1/admin/identities/generate-image/`**

Current behavior: Generate image for identity

New behavior: Generate image AND create/replace session

**Response additions:**
```json
{
  "image_base64": "...",
  "has_active_session": true,
  "session_identity_id": "uuid"
}
```

### New Endpoint: Edit Image

**`POST /api/v1/admin/identities/edit-image/`**

Request:
```json
{
  "user_id": "uuid",          // Required for admin, can test different users
  "edit_prompt": "string"     // What to change
}
```

Response:
```json
{
  "image_base64": "...",
  "has_active_session": true,
  "session_identity_id": "uuid"
}
```

**Error Responses:**
- `400`: No active session - "Please generate an image first before editing"
- `400`: Missing edit_prompt
- `404`: User not found
- `500`: Image generation failed

### Future: Non-Admin Endpoints

When ready for production users:
- `POST /api/v1/identities/generate-image/` - Uses authenticated user
- `POST /api/v1/identities/edit-image/` - Uses authenticated user

These won't need `user_id` parameter - they use the request's authenticated user.

---

## Phase 4: Frontend Changes

### Types

Location: `client/src/types/imageGeneration.ts`

```typescript
// Add to existing types
interface GenerateImageResponse {
  image_base64: string;
  has_active_session: boolean;
  session_identity_id: string | null;
}

interface EditImageRequest {
  user_id: string;
  edit_prompt: string;
}

interface EditImageResponse {
  image_base64: string;
  has_active_session: boolean;
  session_identity_id: string | null;
}
```

### API Layer

Location: `client/src/api/imageGeneration.ts`

Add:
```typescript
export async function editIdentityImage(
  request: EditImageRequest
): Promise<EditImageResponse> {
  // POST to /admin/identities/edit-image/
}
```

### Hook Updates

Location: `client/src/hooks/use-image-generation.ts`

Add:
- `editImage` mutation
- `isEditing` state
- `editError` state
- Track `hasActiveSession` from responses

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
│  │ [Apply Edit]  [Generate New]    │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

**Behavior:**
- "Apply Edit" → Calls edit endpoint, updates displayed image
- "Generate New" → Calls generate endpoint (replaces session), updates displayed image
- Both buttons disabled while loading
- Show loading state during edit

---

## Phase 5: Error Handling

### Backend

| Scenario | Response | Message |
|----------|----------|---------|
| Edit with no session | 400 | "No active image session. Please generate an image first." |
| Edit with empty prompt | 400 | "Edit prompt is required." |
| Session for different identity | 400 | "Current session is for a different identity. Generate a new image to start editing." |
| Gemini API failure | 500 | "Image generation failed. Please try again." |
| Reference images missing | 400 | "Reference images are required for image generation." |

### Frontend

- Display error messages in toast notifications (already using sonner)
- Disable edit UI if `has_active_session` is false
- Clear edit input after successful edit
- Show "No active session" state gracefully

---

## Implementation Order

### Step 1: Database Model
- [ ] Create `ImageGenerationSession` model
- [ ] Run migrations
- [ ] Add admin registration (optional, for debugging)

### Step 2: Service Layer
- [ ] Add `edit_image()` to `GeminiImageService`
- [ ] Add `start_image_session()` to orchestration
- [ ] Add `edit_image_session()` to orchestration
- [ ] Add session management helpers

### Step 3: API Endpoints
- [ ] Modify `generate-image` to create/update session
- [ ] Add `edit-image` endpoint
- [ ] Add proper error responses

### Step 4: Frontend - Types & API
- [ ] Update types for new response fields
- [ ] Add `editIdentityImage` API function

### Step 5: Frontend - Hook & UI
- [ ] Update `useImageGeneration` hook
- [ ] Add edit UI to Images page
- [ ] Wire up edit flow

### Step 6: Testing
- [ ] Test generate → edit → edit flow
- [ ] Test generate → generate (session replacement)
- [ ] Test error cases (no session, empty prompt)
- [ ] Test with different users (admin feature)

---

## Future Considerations

1. **Session expiration**: Consider adding `expires_at` field and cleaning up old sessions
2. **Image storage**: Currently storing base64 in DB. For production scale, might want to store in S3 and reference URL
3. **Edit history**: If users want to "undo" an edit, we'd need to store history
4. **Non-admin endpoints**: When feature is ready for all users, add user-facing endpoints

---

## Questions Resolved

- **Session scope**: Per-user, replaced on any "Generate New" action
- **Reference images**: Sent with every request (generate and edit)
- **Error handling**: User-friendly messages, graceful UI states
- **Storage**: Database (ImageGenerationSession model)
