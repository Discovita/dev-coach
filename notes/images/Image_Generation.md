# Image Generation

We're on the last phase of the first part of the project and arguably the most important: Image Generation.
The Coach works up through I Am Statement creation and then moves on to Image Generation.

For the Visualization Phase to work, we need to work out what the back and forth will look like between the image generation API to get the images we want. Once we have that process figured out, we can embed it into actions and context keys that we'll use in the Visualization Phase prompt to actually plug the image generation functionality into the Coach.

## Initial Attempt with GPT Image

This API has specific features for preserving facial features that will be crucial for this phase to work correctly. The user has to believe they are seeing themselves in the image. If its off even just a little, it can ruin the experience. Maintaining facial features is critical for this phase to work correctly.

## MVP Plan: GPT Image API Integration

### Overview
Use OpenAI's GPT Image API (`gpt-image-1.5` or `gpt-image-1`) with high input fidelity to preserve user faces in generated identity images. This replaces the separate FLUX fine-tuning approach for MVP simplicity.

### Key Requirements
- **Face Preservation**: Use `input_fidelity: "high"` to maintain facial accuracy
- **User Photo Storage**: Store user profile photos for reference
- **Identity Image Generation**: Generate images that combine user face with identity scenarios
- **Integration**: Workflow embedded into visualization phase actions

### Implementation Steps

#### 1. Extend OpenAI Service for GPT Image
- Add GPT Image model support (`gpt-image-1.5`, `gpt-image-1`, `gpt-image-1-mini`)
- Implement `images.edit()` endpoint with `input_fidelity: "high"` parameter
- Support image input (base64 or file paths) for face preservation
- Update validation to handle GPT Image parameters

**Files to modify:**
- `server/services/ai/openai_service/core/image/models.py` - Add GPT Image models
- `server/services/ai/openai_service/core/image/mixin.py` - Add `edit_image()` method
- `server/services/ai/openai_service/core/image/validation.py` - Add GPT Image validation

#### 2. User Photo Storage
- Add `image` field to User model (inherit from `ImageMixin`)
- Create upload endpoint: `PUT /api/v1/users/me/upload-photo/`
- Store user photos in S3 with UUID-based paths

**Files to create/modify:**
- Migration: Add image field to User model
- `server/apps/users/views.py` - Add photo upload endpoint
- `server/apps/users/serializer.py` - Include image URLs in serializer

#### 3. Identity Image Generation Service
- Create service: `server/services/image_generation/identity_image_service.py`
- Function: `generate_identity_image(user_photo_path, identity, prompt)`
- Workflow:
  1. Load user photo from S3
  2. Construct prompt from identity visualization + scenario
  3. Call GPT Image API with `input_fidelity: "high"`
  4. Save generated image to Identity.image field
  5. Return image URLs

**Files to create:**
- `server/services/image_generation/__init__.py`
- `server/services/image_generation/identity_image_service.py`

#### 4. New Action: Generate Identity Image
- Action type: `generate_identity_image`
- Parameters: `identity_id`, `prompt` (optional, uses visualization if not provided)
- Handler: Calls identity image generation service
- Updates Identity.image field with generated image

**Files to create/modify:**
- `server/services/action_handler/models/params.py` - Add `GenerateIdentityImageParams`
- `server/services/action_handler/models/actions.py` - Add `GenerateIdentityImageAction`
- `server/services/action_handler/actions/generate_identity_image.py` - Handler function
- `server/enums/action_type.py` - Add action type enum
- `server/models/CoachChatResponse.py` - Add action to response model

#### 5. Context Key: User Photo
- Context key: `user_photo_url`
- Returns: S3 URL of user's profile photo (or null if not uploaded)
- Used in visualization phase prompt to inform coach about available photo

**Files to create/modify:**
- `server/services/prompt_manager/utils/context/func/get_user_photo_context.py`
- `server/services/prompt_manager/utils/context/get_context_value.py` - Add key mapping
- `server/enums/context_key.py` - Add context key enum

#### 6. Visualization Phase Integration
- Update visualization phase prompt to use `generate_identity_image` action
- Coach workflow:
  1. Check if user has uploaded photo (via `user_photo_url` context)
  2. If photo exists, use `generate_identity_image` action
  3. If no photo, guide user to upload one first
  4. Generate image based on identity visualization text
  5. Allow user to regenerate if unsatisfied
  6. Accept image with `accept_identity_visualization` action

**Files to modify:**
- `server/services/prompt_manager/prompts/phases/identity_visualization.md` - Update prompt instructions

### API Workflow Example

```python
# 1. User uploads photo
PUT /api/v1/users/me/upload-photo/
# Response: User with image URLs

# 2. Coach generates identity image (via action)
{
  "action": "generate_identity_image",
  "params": {
    "identity_id": "uuid",
    "prompt": "A visionary entrepreneur presenting innovative solutions..." # optional
  }
}
# Response: Identity with generated image URLs

# 3. User accepts visualization
{
  "action": "accept_identity_visualization",
  "params": {
    "id": "uuid"
  }
}
```

### Testing Strategy
1. **Unit Tests**: Image generation service with mock API calls
2. **Integration Tests**: Full workflow from photo upload to image generation
3. **Manual Testing**: Verify facial accuracy with real user photos
4. **Edge Cases**: No photo uploaded, generation failures, retry logic

### Future Enhancements (Post-MVP)
- Multi-turn image editing (refine generated images iteratively)
- Image variations (generate multiple options)
- Batch generation for multiple identities
- Consider FLUX fine-tuning for even higher accuracy (if GPT Image insufficient)

### Decision: Revamp vs New Service
**Recommendation**: Extend existing OpenAI service rather than revamping separate image-generation project. Benefits:
- Single codebase maintenance
- Reuse existing S3/image infrastructure
- Direct integration with dev-coach actions
- Simpler deployment

The separate image-generation project can remain for FLUX experimentation but isn't needed for MVP.
