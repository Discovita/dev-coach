"""
Expand Portrait to Scene Script

This script generates a full cinematic scene using:
1. Character views (for face consistency)
2. Generic identity image (for scene/environment reference)

This is Step 4 of the Identity Image Pipeline:
1. Generate Character Views (generate_character_views.py)
2. Generate Generic Identity Image (generate_generic_identity_image.py)
3. Generate Matched Portrait with Clothing (generate_matched_portrait.py) - OPTIONAL
4. Expand Portrait to Scene (this script) <-- YOU ARE HERE

Usage:
    python expand_portrait_to_scene.py

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
# Change these values to match your current working files
# ============================================================================

# The character view images (from Step 1) - for face consistency
CHARACTER_VIEW_IMAGES = [
    "server/services/gemini/images/character_views/casey_multi_05/front.png",
    "server/services/gemini/images/character_views/casey_multi_05/profile_left.png",
    "server/services/gemini/images/character_views/casey_multi_05/profile_right.png",
    "server/services/gemini/images/character_views/casey_multi_05/three_quarter_left.png",
    "server/services/gemini/images/character_views/casey_multi_05/three_quarter_right.png",
]

# The generic identity image (from Step 2) - reference for scene/environment
GENERIC_IDENTITY_IMAGE = "server/services/gemini/images/generic_identity/conductor_01.png"

# Output name for the final scene
OUTPUT_NAME = "conductor_expanded_01"

# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================

OUTPUT_DIR = "server/services/gemini/images/final"

# ============================================================================
# IMAGE CONFIG
# ============================================================================

# Match the aspect ratio of the generic identity image
ASPECT_RATIO = "16:9"
RESOLUTION = "4K"

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
    Build the prompt for generating the scene with character consistency.
    
    Pattern from working scripts:
    - Prompt FIRST
    - Character view images AFTER
    - Scene reference image LAST
    """
    return """The first set of images show a person from multiple angles - use these for character consistency.

The LAST image shows a cinematic scene - recreate this exact scene with the person from the first images.

Requirements:
- The person must look exactly like the person in the reference headshots
- Recreate the same scene, pose, environment, and cinematic lighting from the last image
- Same movie-poster quality aesthetic
- Same dramatic composition

DO NOT include any text or watermarks.
"""


# ============================================================================
# GENERATION
# ============================================================================

def expand_portrait_to_scene(client: genai.Client) -> tuple[str, Image.Image | None]:
    """
    Generate a cinematic scene using character views and scene reference.
    
    Args:
        client: Gemini API client
    
    Returns:
        Tuple of (output_path, PIL Image or None if failed)
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = f"{OUTPUT_DIR}/{OUTPUT_NAME}.png"
    
    print("=" * 60)
    print("GENERATING SCENE WITH CHARACTER CONSISTENCY")
    print("=" * 60)
    print(f"Character views: {len(CHARACTER_VIEW_IMAGES)} images")
    print(f"Scene reference: {GENERIC_IDENTITY_IMAGE}")
    print(f"Output: {output_path}")
    print()
    
    # Load character view images
    character_images = []
    for ref_path in CHARACTER_VIEW_IMAGES:
        if os.path.exists(ref_path):
            character_images.append(Image.open(ref_path))
            print(f"✓ Loaded character view: {ref_path}")
        else:
            print(f"⚠ Character view not found: {ref_path}")
    
    if not character_images:
        print("ERROR: No character view images found!")
        return output_path, None
    
    # Load the scene reference image
    if not os.path.exists(GENERIC_IDENTITY_IMAGE):
        print(f"ERROR: Scene reference not found: {GENERIC_IDENTITY_IMAGE}")
        return output_path, None
    
    scene_image = Image.open(GENERIC_IDENTITY_IMAGE)
    print(f"✓ Loaded scene reference: {GENERIC_IDENTITY_IMAGE}")
    print()
    
    # Build prompt
    prompt = build_prompt()
    print("Prompt:")
    print("-" * 40)
    print(prompt)
    print("-" * 40)
    print()
    
    # Build contents: prompt FIRST, character views, scene reference LAST
    contents = [prompt] + character_images + [scene_image]
    
    # Retry loop with exponential backoff
    retry_delay = INITIAL_RETRY_DELAY
    
    for attempt in range(MAX_RETRIES):
        try:
            print(f"Generating scene (attempt {attempt + 1}/{MAX_RETRIES})...")
            
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
            
            # Check if response has candidates and parts
            if not response.candidates:
                print("WARNING: No candidates in response")
                if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                    print(f"Prompt feedback: {response.prompt_feedback}")
                continue
            
            candidate = response.candidates[0]
            if not candidate.content or not candidate.content.parts:
                print("WARNING: No content/parts in candidate")
                if hasattr(candidate, 'finish_reason'):
                    print(f"Finish reason: {candidate.finish_reason}")
                continue
            
            for part in candidate.content.parts:
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
        print("Usage: python expand_portrait_to_scene.py")
        print()
        print("Generates a cinematic scene using character views for face consistency")
        print("and the generic identity image as a scene reference.")
        print()
        print("Configure inputs by editing the constants at the top of the script:")
        print("  - CHARACTER_VIEW_IMAGES: Character views for face consistency")
        print("  - GENERIC_IDENTITY_IMAGE: Scene reference for environment/composition")
        print("  - OUTPUT_NAME: Name for the output file")
        sys.exit(0)
    
    # Initialize client
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Generate the scene
    output_path, image = expand_portrait_to_scene(client)
    
    # Summary
    print()
    print("=" * 60)
    print("COMPLETE")
    print("=" * 60)
    if image:
        print(f"Generated: {output_path}")
    else:
        print("Failed to generate scene")


if __name__ == "__main__":
    main()
