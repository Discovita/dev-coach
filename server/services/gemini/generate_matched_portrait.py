"""
Generate Matched Portrait Script

This script generates a portrait of the user that matches the head position,
facial expression, lighting, angle, AND CLOTHING from a generic identity image.

This is Step 3 of the Identity Image Pipeline:
1. Generate Character Views (generate_character_views.py)
2. Generate Generic Identity Image (generate_generic_identity_image.py)
3. Generate Matched Portrait (this script) <-- YOU ARE HERE
4. Expand Portrait to Scene (expand_portrait_to_scene.py)

The key matching requirements:
- FACIAL ANGLE: Must match the exact head position, direction, and tilt
- FACIAL EXPRESSION: Must match the expression (smile, serious, etc.)
- LIGHTING: Must match the light direction, shadows, and color grading
- CLOTHING: Must match the clothing/outfit from the scene image

Usage:
    python generate_matched_portrait.py

Output:
    server/services/gemini/images/matched_portraits/<output_name>.png
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
from google import genai
from google.genai import types

# Load environment variables from server/.env
script_path = Path(__file__).resolve()
current = script_path.parent
while current != current.parent:
    if current.name == "server":
        load_dotenv(current / ".env")
        break
    current = current.parent

# ============================================================================
# CONFIGURATION - HARDCODED INPUTS
# Change these values to match your current working files
# ============================================================================

# The generic identity image to match (from Step 2)
GENERIC_IDENTITY_IMAGE = "server/services/gemini/images/generic_identity/conductor_05.png"

# The character view images (from Step 1)
# These provide the reference for the user's face
CHARACTER_VIEW_IMAGES = [
    "server/services/gemini/images/character_views/casey_multi_07/front.png",
    "server/services/gemini/images/character_views/casey_multi_07/three_quarter_left.png",
    "server/services/gemini/images/character_views/casey_multi_07/three_quarter_right.png",
]

# Output name for the matched portrait
OUTPUT_NAME = "conductor_04_matched"

# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================

OUTPUT_DIR = "server/services/gemini/images/matched_portraits"

# ============================================================================
# RETRY CONFIGURATION
# ============================================================================

MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 5  # seconds
RETRY_BACKOFF_MULTIPLIER = 2  # exponential backoff


# ============================================================================
# PROMPT
# ============================================================================

def build_prompt() -> str:
    """
    Build the prompt for generating a matched portrait.
    
    The prompt instructs the model to:
    1. Study the scene image for head position, expression, lighting, and CLOTHING
    2. Use the character views as the ONLY source for the face
    3. Generate a new portrait - NO face blending allowed
    """
    return """I am providing two types of images:

IMAGE 1 (FIRST IMAGE): A "scene reference" image. This person is a STRANGER - ignore their face completely.
IMAGES 2-4 (REMAINING IMAGES): Reference photos of "THE SUBJECT" - this is the person whose face you must reproduce.

YOUR TASK: Generate a portrait of THE SUBJECT (from images 2-4) posed to match the scene reference (image 1).

=== WHAT TO EXTRACT FROM IMAGE 1 (SCENE REFERENCE) ===
ONLY use this image for:
- HEAD ANGLE: Which direction is the head turned? How is it tilted?
- EXPRESSION: Smiling? Serious? Mouth open/closed?
- LIGHTING: Which side is lit? Shadow direction? Color temperature?
- CLOTHING: What outfit? What color? Copy this exactly.
- BACKGROUND: General style/blur of background

COMPLETELY IGNORE the face in image 1. That person is not the subject.

=== WHAT TO EXTRACT FROM IMAGES 2-4 (THE SUBJECT) ===
Use these images for EVERYTHING about the face:
- Exact facial structure, bone structure, face shape
- Exact eyes, nose, mouth, ears, eyebrows
- Exact skin tone, skin texture, facial hair if any
- Exact hair color, style, hairline

=== CRITICAL RULES ===

1. FACE IDENTITY: The output face must be 100% THE SUBJECT from images 2-4. 
   - DO NOT blend faces
   - DO NOT average features between the scene person and the subject
   - DO NOT take any facial features from image 1
   - If you showed this output to someone who knows THE SUBJECT, they must recognize them instantly

2. POSE MATCHING: Match the head angle from image 1:
   - If nose points LEFT in image 1, nose must point LEFT in output
   - If nose points RIGHT in image 1, nose must point RIGHT in output
   - Match the head tilt exactly

3. EXPRESSION: Copy the expression from image 1 onto THE SUBJECT's face

4. LIGHTING: Light THE SUBJECT's face exactly as the scene reference is lit

5. CLOTHING: THE SUBJECT must wear the EXACT same outfit as in image 1

=== OUTPUT FORMAT ===
- Head-and-shoulders portrait (show upper chest for clothing)
- Similar background style to image 1
- NO text, words, or watermarks

Remember: The face in your output should look NOTHING like the person in image 1. 
It should look EXACTLY like the person in images 2-4, just posed/lit/dressed to match image 1.
"""


# ============================================================================
# GENERATION
# ============================================================================

def generate_matched_portrait(client: genai.Client) -> tuple[str, Image.Image | None]:
    """
    Generate a matched portrait using the scene image and character views.
    
    Args:
        client: Gemini API client
    
    Returns:
        Tuple of (output_path, PIL Image or None if failed)
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = f"{OUTPUT_DIR}/{OUTPUT_NAME}.png"
    
    print("=" * 60)
    print("GENERATING MATCHED PORTRAIT")
    print("=" * 60)
    print(f"Scene image: {GENERIC_IDENTITY_IMAGE}")
    print(f"Character views: {len(CHARACTER_VIEW_IMAGES)} images")
    for img_path in CHARACTER_VIEW_IMAGES:
        print(f"  - {img_path}")
    print(f"Output: {output_path}")
    print()
    
    # Load the scene image (generic identity image)
    if not os.path.exists(GENERIC_IDENTITY_IMAGE):
        print(f"ERROR: Scene image not found: {GENERIC_IDENTITY_IMAGE}")
        return output_path, None
    
    scene_image = Image.open(GENERIC_IDENTITY_IMAGE)
    print(f"✓ Loaded scene image: {GENERIC_IDENTITY_IMAGE}")
    
    # Load character view images
    reference_images = []
    for ref_path in CHARACTER_VIEW_IMAGES:
        if os.path.exists(ref_path):
            reference_images.append(Image.open(ref_path))
            print(f"✓ Loaded reference: {ref_path}")
        else:
            print(f"⚠ Reference not found: {ref_path}")
    
    if not reference_images:
        print("ERROR: No character view images found!")
        return output_path, None
    
    print()
    
    # Build prompt
    prompt = build_prompt()
    print("Prompt:")
    print("-" * 40)
    print(prompt)
    print("-" * 40)
    print()
    
    # Build contents: scene image first, then reference images, then prompt
    contents = [scene_image] + reference_images + [prompt]
    
    # Retry loop with exponential backoff
    retry_delay = INITIAL_RETRY_DELAY
    
    for attempt in range(MAX_RETRIES):
        try:
            print(f"Generating matched portrait...")
            
            response = client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                    image_config=types.ImageConfig(
                        aspect_ratio="1:1",
                        image_size="2K"
                    ),
                ),
            )
            
            for part in response.parts:
                if getattr(part, 'thought', False):
                    continue
                if part.text:
                    print(f"[Model] {part.text}")
                if part.inline_data is not None:
                    image = part.as_image()
                    image.save(output_path)
                    print(f"\n✓ Saved: {output_path}")
                    return output_path, image
            
            print("WARNING: No image in response, retrying...")
            
        except Exception as e:
            error_str = str(e)
            is_retryable = "503" in error_str or "UNAVAILABLE" in error_str or "overloaded" in error_str.lower()
            
            if is_retryable and attempt < MAX_RETRIES - 1:
                print(f"⚠ Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
                print(f"  Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= RETRY_BACKOFF_MULTIPLIER
            else:
                print(f"✗ Failed after {attempt + 1} attempts: {e}")
                return output_path, None
    
    return output_path, None


# ============================================================================
# MAIN
# ============================================================================

def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python generate_matched_portrait.py")
        print()
        print("Generates a portrait matching the head position, expression, and lighting")
        print("from a generic identity image, using character views as face reference.")
        print()
        print("Configure inputs by editing the constants at the top of the script:")
        print("  - GENERIC_IDENTITY_IMAGE: The scene to match")
        print("  - CHARACTER_VIEW_IMAGES: The character views for face reference")
        print("  - OUTPUT_NAME: Name for the output file")
        sys.exit(0)
    
    # Initialize client
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Generate the matched portrait
    output_path, image = generate_matched_portrait(client)
    
    # Summary
    print()
    print("=" * 60)
    print("COMPLETE")
    print("=" * 60)
    if image:
        print(f"Generated: {output_path}")
        print()
        print("Next step: Use this matched portrait for Step 4 (Face Swap)")
    else:
        print("Failed to generate matched portrait")


if __name__ == "__main__":
    main()
