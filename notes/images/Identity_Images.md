# Identity Image Generation Pipeline

This document outlines the multi-step process for generating high-quality, personalized Identity Images for users.

## Overview

The goal is to create cinematic, movie-poster quality images of the user living as their chosen Identity (e.g., "Conductor," "Chef," "CEO"). The challenge is maintaining the user's likeness while achieving an artistic, aspirational aesthetic—not a realistic documentary photo.

## The Problem We're Solving

1. **Users upload low-quality photos** - We need to create a high-quality baseline from potentially crappy uploads
2. **Face swapping is unreliable** - Direct face swap approaches with raw photos don't work well
3. **Character consistency loses artistic style** - When we tell the model to use reference photos for character consistency, it tends to generate realistic photos instead of cinematic ones
4. **Left/right confusion** - The model gets confused between "camera's left" vs "subject's left" when generating different angles
5. **Face size affects accuracy** - The smaller the face in the frame, the worse the character consistency
6. **Two face images trigger blocks** - Passing two images that both contain faces triggers safety filters

## Current Best Solution: Matched Portrait Pipeline

The most promising approach is a 4-step pipeline:

### Step 1: Generate Character Views
**Script:** `generate_character_views.py`

Take the user's reference photos (a few clear face shots + one profile is enough) and generate 5 standardized headshots:
- Front, Profile Left, Profile Right, 3/4 Left, 3/4 Right
- White background, consistent clothing, consistent framing

### Step 2: Generate Generic Identity Image
**Script:** `generate_generic_identity_image.py`

Generate a cinematic, movie-poster quality image of the identity using basic physical traits about the user (height, build, hair color, etc.) but NOT worrying about the face. The face can be anyone - we're focused on:
- Scene composition
- Pose and body language
- Clothing and styling
- Lighting and environment
- Cinematic quality

**Critical:** Frame the subject close (waist-up or chest-up) so the face is large in frame. Face should be ~15-25% of image width.

### Step 3: Generate Matched Portrait
**Script:** `generate_matched_portrait.py`

Using the character views and the generic identity image as reference, generate a head-and-shoulders portrait of the USER with:
- Same head angle/direction as the generic image
- Same lighting (direction, color, shadows)
- Same clothing/outfit
- Same expression
- The user's actual face from the character views

This creates a "ready to swap" portrait that matches everything about the generic image except it has the user's face.

### Step 4: Generate Final Image
**Script:** `face_swap_final.py`

Use the matched portrait and the generic identity image to create the final image - the cinematic scene with the user's face.

**Current Status:** This step is still being refined. Direct face swap language triggers safety blocks. We're experimenting with different prompt approaches.

---

## Why This Pipeline

1. **Step 1** creates a quality baseline from potentially crappy user uploads
2. **Step 2** gets the artistic vision right WITHOUT character consistency constraints (model produces best cinematic work when not constrained by face references)
3. **Step 3** bridges the gap - creates a portrait with the correct face that's "pre-matched" to the scene
4. **Step 4** should be simpler because the matched portrait already has the right angle/lighting/clothing

---

## Alternative Approaches Tested

### Text-Described Scene + Character Views
Describe the scene in text only, pass character views, don't pass any scene image.
- **Result:** Works but produces different compositions each time. Can't recreate a specific scene.

### Description-Based Recreation
Generate generic image → Get text description → Regenerate with character views using that description.
- **Result:** Lower quality than the original generic image. Face consistency still imperfect.

### Direct Character Consistency
Generate identity image directly with character view references.
- **Result:** Face is correct, but loses all cinematic quality. Produces documentary-style realistic photos.

### Step 1: Generate Character Views

**Script:** `server/services/gemini/generate_character_views.py`

**Input:** 1-5 reference photos from the user

**Output:** 5 standardized headshot views:
- Front (smiling)
- Profile Left (neutral, nose pointing right in frame)
- Profile Right (neutral, nose pointing left in frame)
- 3/4 Left (smiling, nose angled right)
- 3/4 Right (neutral, nose angled left)

**Key Requirements:**
- All views use consistent framing (head and shoulders, face fills 40-50% of frame)
- Plain white background
- Consistent clothing (light blue collared shirt for men, light blue blouse for women)
- Professional retouching (smooth skin, no blemishes)
- Specified hair color and eye color maintained across all views
- All directions described from viewer's perspective (what appears in the final image)

**Why This Step Matters:**
- Creates a quality baseline from potentially low-quality user uploads
- Gives us multiple angles to work with for different Identity Image poses
- Standardizes the "character" for use in subsequent steps

---

### Step 2: Generate Identity Image (Generic)

**Script:** `server/services/gemini/generate_generic_identity_image.py`

**Input:** Identity details (name, category, I Am statement, visualization description), body description constants

**Output:** A cinematic, movie-poster quality image of a generic person living as this Identity

**Key Requirements:**
- Movie poster quality aesthetic with dramatic, cinematic lighting
- Golden hour or dramatic studio lighting
- Idealized, aspirational composition
- The face can be anyone—we're focused on getting the scene, pose, body, clothing, and environment perfect
- No text or watermarks

**Why This Step Matters:**
- Gets the artistic vision right WITHOUT character consistency constraints
- The model produces its best cinematic work when not constrained by face references
- Creates a "template" that we can describe and recreate

---

### Step 3: Describe Image for Recreation

**Script:** `server/services/gemini/describe_image_for_recreation.py`

**Input:** The generic Identity Image from Step 2

**Output:** A detailed text description (recreation prompt) covering:
- Scene composition and framing
- Lighting (direction, color, mood)
- Subject pose and body language
- Clothing and styling
- Environment and background
- Camera angle and perspective
- Color grading and atmosphere
- Artistic style and quality

**Key Requirements:**
- Description should be detailed enough to recreate the image
- Should NOT describe specific facial features (we're replacing the person)
- Formatted as a prompt that can generate a similar image

**Why This Step Matters:**
- Captures the "recipe" for the cinematic image
- Allows us to recreate the same scene with a different person
- Bridges the gap between "cinematic quality" and "character consistency"

---

### Steps 3-4 Combined: Describe and Regenerate

**Script:** `server/services/gemini/generate_identity_with_description.py`

**Input:**
- The generic Identity Image from Step 2
- The 5 Character Views from Step 1

**Output:** The final Identity Image with the user's face in the cinematic scene

**Process:**
1. Send the generic image to the model and ask for a detailed description
2. Use that description + character views to generate a new image
3. The prompt explicitly tells the model to maintain cinematic quality while using the character's face

**Key Requirements:**
- Description must capture all the cinematic elements (lighting, composition, mood)
- Description must NOT include facial features (we're replacing the person)
- Final generation uses prompt-first content ordering for character consistency

**Why This Step Matters:**
- Combines the best of both worlds: cinematic quality + correct face
- By describing the style explicitly, we can push the model to maintain it even with character references
- All happens in one automated script - no manual steps

---

## Failed Approaches (For Reference)

### Face Swap Approach (Steps 3-4 in old pipeline)
We tried many variations of face swapping:
- "Replace the face with..."
- "Edit to match..."
- "Change only the face..."
- "These are the same person, fix the face..."
- "Recreate with this person..."

**Result:** The model consistently generates a NEW face instead of using the reference. It seems fundamentally incapable of true face swapping.

### Direct Character Consistency
Generating the identity image directly with character view references.

**Result:** The face is correct, but the image loses all cinematic quality. It produces documentary-style realistic photos instead of movie-poster aesthetic.

---

## User Input Requirements

During onboarding, we need to collect from the user:

### Reference Photos

**Ideal Configuration (what produced best results):**
- 3 front-facing photos of their face
- 1 side profile photo

**Minimum Viable:**
- 1 high-quality front-facing photo
- 1 side profile photo

**Photo Requirements:**
- Clear, well-lit photos where face is clearly visible
- Face should take up a significant portion of the frame
- Variety in the front photos helps (slightly different angles, expressions)
- Profile photo helps the model understand the face shape from the side
- Higher quality photos = better results (but the pipeline can work with lower quality)

**Why This Mix Works:**
- Multiple front photos give the model redundant information about the face from the primary angle
- The side profile is crucial for generating accurate profile and 3/4 views
- Without a profile reference, the model has to "guess" what the person looks like from the side

### Other Required Information

- Gender (man/woman)
- Hair color
- Eye color

### Optional/Derived

- Ethnicity (can potentially be detected from photos)
- Build/body type (for body description in prompts)

---

## Technical Considerations

### Content Ordering for Gemini API
- For character consistency: `[prompt] + [reference_images]`
- For image editing: `[scene_image] + [reference_images] + [prompt]`

### Retry Logic
- 503/UNAVAILABLE errors are common when model is overloaded
- Implement exponential backoff: 5s → 10s → 20s
- Max 3 retries per image

### Quality Control
- The model sometimes produces incorrect angles (e.g., 3/4 when asked for profile)
- May need to regenerate multiple times to get correct output
- Consider adding validation step or allowing user to request regeneration

---

## Future Enhancements

1. **Automated validation** - Use vision model to verify generated views match requirements
2. **Style transfer** - Allow users to specify artistic style preferences
3. **Batch generation** - Generate multiple Identity Images in parallel
4. **Caching** - Store Character Views so they don't need to be regenerated for each Identity

---

## Current Scripts

These are development/testing scripts, not production code:

**Core Pipeline Scripts (Steps 1-4):**
- `generate_character_views.py` - Step 1: Generate standardized character views from user photos (WORKS WELL)
- `generate_generic_identity_image.py` - Step 2: Generate cinematic identity image with generic face (WORKS WELL)
- `generate_matched_portrait.py` - Step 3: Generate portrait matching scene's angle/lighting/clothing with user's face (WORKS - produces good matched portraits)
- `face_swap_final.py` - Step 4: Combine matched portrait with scene to create final image (IN PROGRESS - dealing with safety filter blocks)

**Experimental:**
- `expand_portrait_to_scene.py` - Alternative approach: expand portrait outward into full scene (blocked by safety filters)

**Utility Scripts:**
- `generate_identity_with_description.py` - Describe image → Regenerate with character views (alternative approach)
- `describe_image_for_recreation.py` - Get description only (for debugging/manual use)

**Deprecated/Failed:**
- `face_swap_matched_view.py` - Old combined pipeline
- `face_swap.py` - Original face swap approach
- `generate_identity_image.py` - Direct character consistency (face correct, style wrong)

---

## Key Learnings

1. **Describe final image, not camera position** - "Nose pointing to the right side of the frame" works better than "camera at 90 degrees to their left"

2. **Separate scene creation from face matching** - Trying to do both at once causes the model to compromise on artistic style

3. **Face swapping doesn't work** - Despite many prompt variations, Gemini will not reliably swap faces. It generates new faces instead of using references.

4. **Character consistency kills cinematic style** - When given face references, the model shifts from "movie poster" to "documentary photo" style

5. **Description-based recreation may work** - Get the model to describe its own cinematic output, then use that description + character refs to recreate

6. **Multiple reference images help** - 3-5 reference photos give better character consistency than a single photo

7. **Specify expressions explicitly** - Default is neutral/closed mouth; must explicitly request smiling

8. **Consistent framing matters** - Specify exact framing requirements to avoid zoom/distance variation

9. **CRITICAL: Face size determines accuracy** - The closer/larger the subject's face is in the frame, the more accurately the model maintains character consistency. When the face is small (distant shots, wide compositions), the model struggles to apply the reference face correctly. For best results:
   - Frame subjects from waist-up or chest-up, NOT full body distant shots
   - Face should occupy roughly 15-25% of the image width
   - "Movie poster close-up" compositions work better than "wide establishing shots"
   - This applies to both the generic identity image AND the final character-consistent output

10. **Two images with faces triggers blocks** - Passing two images that both contain faces (e.g., a scene image + a portrait) triggers Gemini's safety filters with `BlockedReason.OTHER`. The model interprets this as potential face manipulation/deepfake attempt. Workarounds:
    - Use character views (standardized headshots on white backgrounds) instead of generated portraits
    - Don't pass the scene image at all - describe the scene in text instead
    - Avoid any language about "replacing" or "swapping" faces

11. **Left/right mirroring in matched portraits** - When generating a portrait to match a scene's angle, the model sometimes mirrors the direction (e.g., nose pointing left in scene but right in portrait). Fix by being extremely explicit: "If the nose points toward the LEFT edge of the frame, the output nose must also point toward the LEFT edge." Use "edge of frame" language, not "left/right" which is ambiguous.

12. **Retry logic should be infinite for 503 errors** - The Gemini API frequently returns 503 UNAVAILABLE when overloaded. Instead of limited retries with exponential backoff, use infinite retries with a fixed 3-second delay. The model will eventually respond.

---

## Session Summary (January 2026)

### What We Built This Session

**4-Step Pipeline:**
1. `generate_character_views.py` - Takes user photos, generates 5 standardized headshots (WORKING)
2. `generate_generic_identity_image.py` - Generates cinematic scene with generic face, close framing (WORKING)
3. `generate_matched_portrait.py` - Generates portrait of user with same angle/lighting/clothing as generic image (WORKING)
4. `face_swap_final.py` - Creates final image combining matched portrait with scene (IN PROGRESS)

### Key Discoveries

1. **Face size is critical** - Added FRAMING REQUIREMENTS to generic image generation. Face should be 15-25% of image width. Close-up compositions work much better than wide shots.

2. **Two face images trigger safety blocks** - Passing a scene image + portrait together triggers `BlockedReason.OTHER`. The model thinks it's a deepfake attempt.

3. **Left/right mirroring happens** - The matched portrait sometimes mirrors the direction. Fixed by being explicit: "If nose points toward LEFT edge of frame, output must also point toward LEFT edge."

4. **Character views don't trigger blocks** - Standardized headshots on white backgrounds are treated differently than "two images with faces in scenes."

5. **Infinite retry for 503 errors** - Changed from exponential backoff to simple 3-second delay infinite retry. Model eventually responds.

### Current Blocker

Step 4 (final image generation) is blocked by safety filters when passing:
- Scene image (generic identity with a face) + Matched portrait (user's face)

The model interprets this as face manipulation. We need to find a prompt/approach that:
- Uses both images as reference
- Doesn't trigger the deepfake detection
- Actually applies the user's face (not just copying the scene)

### Approaches Still To Try

- Different prompt framing (avoid any "swap/replace" language)
- Multi-turn conversation for iterative refinement
- Passing more character views instead of just the matched portrait
- Using the scene image for environment only, describing the face separately
- Testing if the matched portrait on its own (without scene image) can recreate the scene
