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

---

## Attempt 2: Gemini 3 Pro Image Preview (Nano Banana Pro)

**Date**: January 2026  
**Status**: ABANDONED - Inconsistent facial likeness

### Problem Statement
The current identity image generation flow takes 5 user-uploaded reference photos and passes them directly to the image model with the identity prompt. Results were inconsistent - sometimes the generated person looked nothing like the user, especially when users uploaded low-quality selfies.

### Proposed Solution: Two-Stage Avatar System
Instead of passing raw reference photos directly to identity generation, create an intermediate "avatar" image first:

1. **Stage 1 - Avatar Generation** (one-time): Take user's 5 reference photos → Generate a high-quality, idealized "avatar" headshot and full-body shot
2. **Stage 2 - Identity Generation** (per identity): Use the approved avatar as the single reference for all identity images

The avatar would be:
- A professional headshot (shoulders up, neutral background)
- An idealized/retouched version (glamour photography style, smooth skin, no wrinkles/stubble, 5-10 years younger)
- Stored as a `UserAvatar` model with `OneToOneField` to User

### What We Built
Created `server/services/gemini/generate_avatar.py` - a test script for avatar generation:

**Features:**
- Generates headshot from 5 reference photos using Gemini 3 Pro Image Preview
- Generates full-body shot from the headshot
- Auto-incrementing paired filenames (`casey_avatar_headshot_nb_01.png`, `casey_avatar_fullbody_nb_01.png`)
- `--multi` flag to generate 3 candidates at 1K quality for comparison
- Shows model's "thinking" process (interim images)
- Accepts existing headshot path to skip step 1

**Prompt Strategy:**
```
HEADSHOT_PROMPT = """Look at the reference photos provided. Study this person's face carefully - their face shape, eyes, nose, mouth, jawline, hairline, and all distinctive features.

Now create a professional headshot of THIS EXACT PERSON.

Shoulders up, facing camera, neutral gray background.
Warm confident smile, bright eyes.
Clean studio lighting with soft edge lighting for depth.

CRITICAL: The output must be recognizably THE SAME PERSON from the reference photos. Do not generate a generic face. Use the reference photos as your guide for every facial feature.

Style: Glamour photography with tasteful retouching.
- Smooth, flawless skin - no visible pores, wrinkles, or blemishes
- Even hair color - no gray or salt-and-pepper, natural consistent tone
- Bright, youthful eyes
- Polished and aspirational - the best version of this specific person
- They should look 5-10 years younger and refreshed

This person should look at the result and immediately recognize themselves.
"""
```

### Technical Discoveries

1. **Content Order Matters**: Putting images BEFORE the prompt text in the API call seemed to improve likeness (images first, then prompt)

2. **PIL Image Format Issue**: When passing a generated image to a subsequent API call, you must save it to disk first and reload with `Image.open()` - passing the raw `part.as_image()` result causes `ValueError: file uri and mime_type are required`

3. **Thinking Mode**: Gemini 3 Pro uses a "thinking" process with interim images. Access via `part.thought` attribute. Thinking images are not charged.

4. **Image Config Options**:
   - `image_size`: "1K", "2K", "4K" (must be uppercase K)
   - `aspect_ratio`: "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"
   - Can request multiple images in prompt but model may not always comply

### Why It Failed
**Non-deterministic likeness**: The model is fundamentally inconsistent at preserving facial features from reference images.

- Run 1: Generated a decent likeness
- Run 2: Similar style but face drifting  
- Run 3: Completely different person
- Run 4: Yet another different person

Same prompt, same reference images, wildly different faces each time. The model sometimes pays attention to reference photos and sometimes just generates a generic professional headshot.

**Key insight**: Gemini's image generation doesn't have a reliable mechanism to "lock in" facial features from reference images. Unlike fine-tuning approaches (FLUX LoRA) or GPT Image's `input_fidelity: "high"`, there's no parameter to force the model to preserve specific facial characteristics.

### Artifacts Created
- `server/services/gemini/generate_avatar.py` - Test script (kept for reference)
- `server/services/gemini/images/reference/` - Reference photos
- `server/services/gemini/images/casey_avatar_headshot_nb_*.png` - Generated test images
- `server/services/gemini/images/casey_avatar_fullbody_nb_*.png` - Generated test images

### Lessons Learned
1. **Gemini is non-deterministic for faces**: Without fine-tuning or explicit face-locking mechanisms, you cannot reliably reproduce a specific person's face
2. **Two-stage approach is sound**: The concept of generating a high-quality avatar first, then using it for identity images, is still valid - just needs a model that can actually preserve faces
3. **Prompt engineering has limits**: No amount of "CRITICAL: same person" instructions can overcome the model's fundamental inability to consistently reference input images for facial features
4. **Consider alternatives**: GPT Image with `input_fidelity: "high"` or FLUX fine-tuning may be necessary for reliable face preservation

### Next Steps
- Try GPT Image API with `input_fidelity: "high"` parameter
- If that fails, consider FLUX fine-tuning approach
- The avatar concept can be reused with whichever model works

---

## Attempt 3: Generic Image + Face Swap (Proposed)

**Date**: January 2026  
**Status**: IDEA - Not yet implemented

### Core Concept
Stop trying to generate the user's face directly. Instead:

1. **Generate a generic identity image** - Don't worry about the face at all, just get the scene/pose/clothing right
2. **Face swap** - Use a separate prompt/service to swap the user's face onto the generic image

We tried this approach before with other models/services and the execution was terrible. But Nano Banana Pro seems to be very good at face swapping specifically, so it's worth revisiting.

### Why This Might Work
- Separates two hard problems: scene generation and face preservation
- Face swapping is a well-defined task that models can do reliably
- Generic image generation is much easier when you don't need a specific face
- Gemini/Nano Banana Pro has shown good results with face-related editing tasks

### New Features Required

#### 1. Face-Cropped Reference Images
**Problem**: Users upload full photos but we only need their face for face swapping.

**Solution**: Add a crop/zoom UI when uploading reference images:
- User uploads photo
- UI shows the image with a square overlay (like Google profile photo picker)
- User can zoom in/out and pan to position their face in the square
- On save, we crop to just the square area
- Store only the cropped face image as the reference

This ensures we have clean, face-only reference images for the swap step.

**UI Pattern**: Similar to profile photo croppers everywhere - circle or square overlay, pinch-to-zoom, drag to position.

#### 2. Body Description Questions
**Problem**: If we're generating a generic person first, we need to know what body type to generate so it matches the user reasonably well.

**Solution**: Simple questionnaire during onboarding or before first image generation:

**Gender** (affects which questions appear):
- Man
- Woman
- Non-binary / Other

**Height** (simple categories, not exact numbers):
- Short
- Below average
- Average
- Above average
- Tall

**Build** (careful wording to be respectful):
- Slim / Slender
- Athletic / Fit
- Average
- Curvy / Stocky
- Plus-size / Large

**Ethnicity/Appearance** (dropdown, for skin tone and features):
- Options TBD - need to be inclusive and respectful
- Could be simple like: Light, Medium, Dark skin tone
- Or more specific ethnic categories

**Design Principles**:
- No sliders or exact numbers (weight in lbs is a no-go, especially for women)
- Simple dropdown/radio selections
- Respectful language that doesn't make anyone feel bad
- 3-5 options per category is probably right
- Can be skipped with reasonable defaults

#### 3. Two-Step Generation Flow

**Step 1: Generate Generic Identity Image**
```
Prompt: "A [height] [build] [ethnicity] [gender] person as [identity description]..."
```
- Uses body description to generate appropriate body type
- Face doesn't matter - can be generic or even blurred/obscured
- Focus on getting the scene, pose, clothing, and vibe right

**Step 2: Face Swap**
```
Prompt: "Replace the face in this image with the face from these reference photos. 
Preserve the exact pose, lighting, and expression direction from the original image.
The face should look natural and integrated into the scene."
```
- Input: Generated identity image + user's cropped face reference(s)
- Output: Same image but with user's face

### Workflow

1. **Onboarding** (one-time):
   - User answers body description questions
   - User uploads 5 reference photos with face cropping UI
   - Data stored on User model

2. **Identity Image Generation** (per identity):
   - Generate generic image using body description + identity prompt
   - Face swap using stored face references
   - Show result to user
   - Allow regeneration if needed

### Open Questions

- How many face references do we need for good face swapping? (1? 3? 5?)
  - Right now users can upload up to 5 reference images.
- Should we let users skip body questions and use defaults?
  - Initially, no.
- What's the right set of ethnicity/appearance options?
  - We need to be inclusive and respectful.
  - Going for basic options at the start for development purposes
- Do we need different body description options for men vs women?
  - Right now, no. Go with the same choices. Let the image model handle the differences between genders.
- Should the face swap be automatic or a separate user-triggered step?
  - this will be part of the same flow. The generate image will be a two step function that generates the image and then swaps the face - passing off the final image to the user.
  - For development purposes, we need to save the intermediate image to a file so we can see it.

### Risks

- Face swap quality might still be inconsistent
- Two-step process is slower and more expensive (2 API calls per image)
- Body description categories might not capture enough variation
- Users might find the body questions intrusive

### Why Not Just Use GPT Image?
Still worth trying GPT Image with `input_fidelity: "high"` first - if it works, it's simpler than this two-step approach. This is the fallback plan if direct face preservation doesn't work with any model.
