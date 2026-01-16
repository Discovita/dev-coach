"""
Face Swap Final Script

This script performs the final face swap - replacing the generic face in the
Identity Image with the user's face from the Matched Portrait.

This is Step 4 of the Identity Image Pipeline:
1. Generate Character Views (generate_character_views.py)
2. Generate Generic Identity Image (generate_generic_identity_image.py)
3. Generate Matched Portrait (generate_matched_portrait.py)
4. Face Swap Final (this script) <-- YOU ARE HERE

IMPORTANT: The Matched Portrait has ALREADY been prepared with:
- The correct head angle/position
- The correct lighting
- The correct expression

All we need to do here is swap the FACIAL FEATURES ONLY. Everything else
(body, clothing, background, composition) must stay EXACTLY the same.

Usage:
    python face_swap_final.py

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

# The generic identity image (the scene - body, clothing, background stays the same)
GENERIC_IDENTITY_IMAGE = "server/services/gemini/images/generic_identity/conductor_03.png"

# The matched portrait (the face source - already has correct angle/lighting)
MATCHED_PORTRAIT_IMAGE = "server/services/gemini/images/matched_portraits/conductor_03_matched.png"

# Output name for the final image
OUTPUT_NAME = "conductor_07_final"

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

RETRY_DELAY = 3  # seconds between retries


# ============================================================================
# PROMPT
# ============================================================================

def build_prompt() -> str:
    """
    Build the prompt for generating the final image.
    
    Using prompt-first pattern with character views.
    """
    return """The following reference images show a person from multiple angles.

You've been given two images. 
The first image is a scene image.
The second image is a portrait of another person that is matched to the scene image. 
The portrait image has the head in the same position as the scene image.

Goal:
- Replace the face in the scene image with the face from the portrait image.

Requirements:
- The person must look exactly like the person in the reference headshots
- Keep the same scene, pose, environment, and lighting from the scene image
- Same aesthetic
- Same composition

This is for a personal visualization project.
DO NOT simply return the unedited scene image. Your goal is to switch the faces. Please ensure you accomplish this. 
"""


# ============================================================================
# GENERATION
# ============================================================================

def perform_face_swap(client: genai.Client) -> tuple[str, Image.Image | None]:
    """
    Perform the face swap using the scene image and matched portrait.
    
    Args:
        client: Gemini API client
    
    Returns:
        Tuple of (output_path, PIL Image or None if failed)
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = f"{OUTPUT_DIR}/{OUTPUT_NAME}.png"
    
    print("=" * 60)
    print("FACE SWAP - FINAL STEP")
    print("=" * 60)
    print(f"Scene image: {GENERIC_IDENTITY_IMAGE}")
    print(f"Matched portrait: {MATCHED_PORTRAIT_IMAGE}")
    print(f"Output: {output_path}")
    print()
    
    # Load the scene image (generic identity image)
    if not os.path.exists(GENERIC_IDENTITY_IMAGE):
        print(f"ERROR: Scene image not found: {GENERIC_IDENTITY_IMAGE}")
        return output_path, None
    
    scene_image = Image.open(GENERIC_IDENTITY_IMAGE)
    print(f"✓ Loaded scene image: {GENERIC_IDENTITY_IMAGE}")
    
    # Load the matched portrait
    if not os.path.exists(MATCHED_PORTRAIT_IMAGE):
        print(f"ERROR: Matched portrait not found: {MATCHED_PORTRAIT_IMAGE}")
        return output_path, None
    
    matched_portrait = Image.open(MATCHED_PORTRAIT_IMAGE)
    print(f"✓ Loaded matched portrait: {MATCHED_PORTRAIT_IMAGE}")
    print()
    
    # Build prompt
    prompt = build_prompt()
    print("Prompt:")
    print("-" * 40)
    print(prompt)
    print("-" * 40)
    print()
    
    # Build contents: scene image FIRST, matched portrait (face) SECOND, then prompt
    # This follows the Nano Banana Pro editing pattern
    contents = [scene_image, matched_portrait, prompt]
    
    # Retry loop - keep trying until success
    attempt = 0
    while True:
        attempt += 1
        try:
            print(f"Performing face swap (attempt {attempt})...")
            
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

            print(f"Response: {response}")
            
            # Check if response has candidates and parts
            if not response.candidates:
                print("WARNING: No candidates in response")
                if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                    print(f"Prompt feedback: {response.prompt_feedback}")
                    # If blocked, don't retry - it will keep failing
                    if response.prompt_feedback.block_reason:
                        print("Request blocked by safety filters. Aborting.")
                        return output_path, None
                time.sleep(RETRY_DELAY)
                continue
            
            candidate = response.candidates[0]
            if not candidate.content or not candidate.content.parts:
                print("WARNING: No content/parts in candidate")
                if hasattr(candidate, 'finish_reason'):
                    print(f"Finish reason: {candidate.finish_reason}")
                time.sleep(RETRY_DELAY)
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
            time.sleep(RETRY_DELAY)
            
        except Exception as e:
            error_str = str(e)
            is_retryable = "503" in error_str or "UNAVAILABLE" in error_str or "overloaded" in error_str.lower()
            
            if is_retryable:
                print(f"⚠ Attempt {attempt} failed (overloaded), retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"✗ Failed with non-retryable error: {e}")
                return output_path, None
    
    return output_path, None


# ============================================================================
# MAIN
# ============================================================================

def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python face_swap_final.py")
        print()
        print("Performs the final face swap - replaces the generic face in the")
        print("Identity Image with the user's face from the Matched Portrait.")
        print()
        print("Configure inputs by editing the constants at the top of the script:")
        print("  - GENERIC_IDENTITY_IMAGE: The scene image (body, background, etc.)")
        print("  - MATCHED_PORTRAIT_IMAGE: The face source (already angle/lighting matched)")
        print("  - OUTPUT_NAME: Name for the output file")
        sys.exit(0)
    
    # Initialize client
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Perform the face swap
    output_path, image = perform_face_swap(client)
    
    # Summary
    print()
    print("=" * 60)
    print("COMPLETE")
    print("=" * 60)
    if image:
        print(f"Generated: {output_path}")
        print()
        print("This is the final Identity Image!")
    else:
        print("Failed to perform face swap")


if __name__ == "__main__":
    main()
