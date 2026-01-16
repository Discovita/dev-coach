"""
Generate Identity Image with Description-Based Recreation

This script implements the full pipeline:
1. Take a generic identity image (cinematic, movie-poster quality)
2. Get a detailed description of the image from the model
3. Use that description + character views to regenerate with the correct person

This solves the problem where:
- Direct character consistency loses cinematic style
- Face swapping doesn't work (model ignores reference faces)

By describing the cinematic image first, then using that description WITH
character references, we can (hopefully) get both cinematic quality AND
the correct face.

Usage:
    python generate_identity_with_description.py

Output:
    server/services/gemini/images/final/<output_name>.png
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
# ============================================================================

# The generic identity image to recreate (from Step 2)
GENERIC_IDENTITY_IMAGE = "server/services/gemini/images/generic_identity/conductor_01.png"

# The character view images (from Step 1)
CHARACTER_VIEW_IMAGES = [
    "server/services/gemini/images/character_views/casey_multi_05/front.png",
    "server/services/gemini/images/character_views/casey_multi_05/profile_left.png",
    "server/services/gemini/images/character_views/casey_multi_05/profile_right.png",
    "server/services/gemini/images/character_views/casey_multi_05/three_quarter_left.png",
    "server/services/gemini/images/character_views/casey_multi_05/three_quarter_right.png",
]

# Output name
OUTPUT_NAME = "conductor_desc_01"

# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================

OUTPUT_DIR = "server/services/gemini/images/final"

# Match the aspect ratio and resolution of the generic identity image
ASPECT_RATIO = "16:9"
RESOLUTION = "4K"

# ============================================================================
# RETRY CONFIGURATION
# ============================================================================

MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 5
RETRY_BACKOFF_MULTIPLIER = 2


# ============================================================================
# STEP 1: GET DESCRIPTION OF GENERIC IMAGE
# ============================================================================

def get_description_prompt() -> str:
    """Prompt to get a detailed description of the image for recreation."""
    return """Analyze this image and create a detailed description that could be used to recreate it with a different person.

Describe everything that makes this image look the way it does:
- Scene, setting, and environment
- Composition and framing
- Lighting (direction, quality, color)
- Subject's pose, body position, and expression
- Clothing and styling
- Background elements
- Camera angle and perspective
- Colors, mood, and atmosphere
- Any artistic style or quality characteristics

DO NOT describe the person's specific facial features (face shape, eyes, nose, mouth) - we want to replace them with a different person.

Format your response as a single prompt that could recreate this exact image with a different person. Start with "An image of a person..." and include all the important visual details.
"""


def get_image_description(client: genai.Client, image: Image.Image) -> str | None:
    """
    Get a detailed description of the image from the model.
    
    Args:
        client: Gemini API client
        image: The image to describe
    
    Returns:
        The description text, or None if failed
    """
    print("=" * 60)
    print("STEP 1: GETTING IMAGE DESCRIPTION")
    print("=" * 60)
    
    prompt = get_description_prompt()
    contents = [image, prompt]
    
    retry_delay = INITIAL_RETRY_DELAY
    
    for attempt in range(MAX_RETRIES):
        try:
            print("Analyzing image...")
            
            response = client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT"],
                ),
            )
            
            for part in response.parts:
                if part.text:
                    print("✓ Got description")
                    print()
                    print("Description:")
                    print("-" * 40)
                    print(part.text)
                    print("-" * 40)
                    print()
                    return part.text
            
            print("WARNING: No text in response, retrying...")
            
        except Exception as e:
            error_str = str(e)
            is_retryable = "503" in error_str or "UNAVAILABLE" in error_str or "overloaded" in error_str.lower()
            
            if is_retryable and attempt < MAX_RETRIES - 1:
                print(f"⚠ Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
                print(f"  Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= RETRY_BACKOFF_MULTIPLIER
            else:
                print(f"✗ Failed: {e}")
                return None
    
    return None


# ============================================================================
# STEP 2: GENERATE WITH CHARACTER CONSISTENCY
# ============================================================================

def build_recreation_prompt(description: str) -> str:
    """
    Build the final prompt using the description and character consistency.
    
    Uses patterns from successful character consistency prompts:
    - "100% identical facial features"
    - "preserve_original: true"
    - "exactly the same as the reference image"
    
    Args:
        description: The detailed description from Step 1
    
    Returns:
        The full prompt for image generation
    """
    return f"""Create this scene with the person from the reference images:

{description}

FACE REQUIREMENTS (CRITICAL - 100% accuracy required):
- Keep the facial features of the person in the reference images EXACTLY consistent
- 100% identical facial features, bone structure, skin tone
- The face must remain exactly the same as the reference images
- Do not change the face in any way

The scene, lighting, pose, clothing, and environment should match the description above.
"""


def generate_with_character(
    client: genai.Client,
    description: str,
    character_images: list[Image.Image]
) -> tuple[str, Image.Image | None]:
    """
    Generate the final image using description + character views.
    
    Args:
        client: Gemini API client
        description: The scene description from Step 1
        character_images: List of character view PIL Images
    
    Returns:
        Tuple of (output_path, PIL Image or None if failed)
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = f"{OUTPUT_DIR}/{OUTPUT_NAME}.png"
    
    print("=" * 60)
    print("STEP 2: GENERATING WITH CHARACTER CONSISTENCY")
    print("=" * 60)
    print(f"Using {len(character_images)} character views")
    print(f"Output: {output_path}")
    print()
    
    prompt = build_recreation_prompt(description)
    print("Recreation prompt:")
    print("-" * 40)
    print(prompt)
    print("-" * 40)
    print()
    
    # Content order: prompt first, then character images (for character consistency)
    contents = [prompt] + character_images
    
    retry_delay = INITIAL_RETRY_DELAY
    
    for attempt in range(MAX_RETRIES):
        try:
            print("Generating final image...")
            
            response = client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                    image_config=types.ImageConfig(
                        aspect_ratio=ASPECT_RATIO,
                        image_size=RESOLUTION
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
                print(f"✗ Failed: {e}")
                return output_path, None
    
    return output_path, None


# ============================================================================
# MAIN
# ============================================================================

def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python generate_identity_with_description.py")
        print()
        print("Full pipeline: Describe generic image → Regenerate with character views")
        print()
        print("Configure by editing the constants at the top of the script:")
        print("  - GENERIC_IDENTITY_IMAGE: The cinematic image to recreate")
        print("  - CHARACTER_VIEW_IMAGES: The character views for face consistency")
        print("  - OUTPUT_NAME: Name for the output file")
        sys.exit(0)
    
    # Initialize client
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    print("=" * 60)
    print("IDENTITY IMAGE GENERATION")
    print("Description-Based Recreation Pipeline")
    print("=" * 60)
    print(f"Generic image: {GENERIC_IDENTITY_IMAGE}")
    print(f"Character views: {len(CHARACTER_VIEW_IMAGES)} images")
    print(f"Output: {OUTPUT_DIR}/{OUTPUT_NAME}.png")
    print()
    
    # Load generic identity image
    if not os.path.exists(GENERIC_IDENTITY_IMAGE):
        print(f"ERROR: Generic image not found: {GENERIC_IDENTITY_IMAGE}")
        sys.exit(1)
    
    generic_image = Image.open(GENERIC_IDENTITY_IMAGE)
    print(f"✓ Loaded generic image: {GENERIC_IDENTITY_IMAGE}")
    
    # Load character views
    character_images = []
    for path in CHARACTER_VIEW_IMAGES:
        if os.path.exists(path):
            character_images.append(Image.open(path))
            print(f"✓ Loaded character view: {path}")
        else:
            print(f"⚠ Character view not found: {path}")
    
    if not character_images:
        print("ERROR: No character views found!")
        sys.exit(1)
    
    print()
    
    # Step 1: Get description
    description = get_image_description(client, generic_image)
    
    if not description:
        print("ERROR: Failed to get image description")
        sys.exit(1)
    
    # Step 2: Generate with character consistency
    output_path, final_image = generate_with_character(client, description, character_images)
    
    # Summary
    print()
    print("=" * 60)
    print("COMPLETE")
    print("=" * 60)
    if final_image:
        print(f"Generated: {output_path}")
        print()
        print("Compare this with the original generic image to see if:")
        print("  1. The face matches the character views")
        print("  2. The cinematic quality is preserved")
    else:
        print("Failed to generate final image")


if __name__ == "__main__":
    main()
