"""
Generate Identity Image Script (Direct Approach)

This script generates an identity image directly from character reference images.
Instead of creating a generic image and trying to face-swap, we use Gemini's
"character consistency" feature to generate the scene with the subject's face
from the start.

Key insight from Gemini docs:
- Up to 5 images of humans can be used to maintain character consistency
- The model can place a person from reference images into a new scene

This is an ALTERNATIVE approach to the multi-step pipeline:
1. Generate Character Views (generate_character_views.py) - same
2. Generate Identity Image (this script) <-- DIRECT GENERATION

Usage:
    python generate_identity_image.py [--output <name>]

Examples:
    python generate_identity_image.py
    python generate_identity_image.py --output conductor_01

Output:
    server/services/gemini/images/identity/<output_name>.png
"""

import os
import sys
import glob
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
# CONFIGURATION
# ============================================================================

OUTPUT_DIR = "server/services/gemini/images/identity"

# Character view images (from Step 1) - these are the reference for the subject's face
CHARACTER_VIEW_IMAGES = [
    "server/services/gemini/images/character_views/jason_multi_02/front.png",
    "server/services/gemini/images/character_views/jason_multi_02/three_quarter_left.png",
    "server/services/gemini/images/character_views/jason_multi_02/three_quarter_right.png",
]

# ============================================================================
# RETRY CONFIGURATION
# ============================================================================

RETRY_DELAY = 3  # seconds between retries

# ============================================================================
# IMAGE CONFIG CONSTANTS
# ============================================================================

# Aspect ratio options: "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"
ASPECT_RATIO = "16:9"

# Resolution options: "1K", "2K", "4K"
RESOLUTION = "2K"

# ============================================================================
# IDENTITY CONSTANTS
# These define what identity/role the person is visualized as
# ============================================================================

# Identity Name: The name of the identity being visualized
IDENTITY_NAME = "Castle Builder"

# Category: The identity category (e.g., "Passions & Talents", "Career & Purpose", etc.)
IDENTITY_CATEGORY = "Romantic Relation"

# I Am Statement: Optional - the "I Am" statement for this identity
IDENTITY_I_AM_STATEMENT = "I am a Castle Builder and I build a space that is safe for our nervous systems and I create a space for love, kindness, and safety to grow. I am going to build a castle with a moat on Hawaiian soil using agricultural land for our relationship to grow."

# Visualization: Optional - the visualization/scene description for this identity
IDENTITY_VISUALIZATION = """
He's on a hill with the castle over Hawaiian agricultural land with view of the ocean
He's wearing a linen button down shirt.
He's proud and calm.
"""

# Notes: Optional - list of notes about this identity
IDENTITY_NOTES = None  # e.g., ["Focus on leadership", "Emphasize creativity"]


# ============================================================================
# UTILITIES
# ============================================================================

def get_next_run_number() -> int:
    """Find the next available numbered output file."""
    if not os.path.exists(OUTPUT_DIR):
        return 1
    
    existing_files = glob.glob(f"{OUTPUT_DIR}/[0-9][0-9].png")
    
    if not existing_files:
        return 1
    
    numbers = []
    for f in existing_files:
        basename = os.path.basename(f)
        try:
            num = int(basename.replace(".png", ""))
            numbers.append(num)
        except ValueError:
            continue
    
    return max(numbers) + 1 if numbers else 1


def get_identity_context() -> str:
    """
    Format identity context for the prompt.
    """
    parts = [
        f'Identity Name: "{IDENTITY_NAME}"',
        f"Category: {IDENTITY_CATEGORY}",
    ]
    
    if IDENTITY_I_AM_STATEMENT:
        parts.append(f"I Am Statement: {IDENTITY_I_AM_STATEMENT}")
    
    if IDENTITY_VISUALIZATION:
        parts.append(f"Visualization: {IDENTITY_VISUALIZATION}")
    
    if IDENTITY_NOTES:
        notes_str = "; ".join(IDENTITY_NOTES)
        parts.append(f"Notes: {notes_str}")
    
    return "\n".join(parts)


def build_prompt() -> str:
    """
    Build the prompt for generating an identity image with the subject.
    
    Key approach: Use Gemini's character consistency feature.
    The reference images show WHO the person is - their exact face.
    The prompt describes the SCENE they should be placed into.
    """
    identity_context = get_identity_context()
    
    return f"""I am providing reference photos of a specific person (THE SUBJECT).
Your task is to create a DREAM VISUALIZATION - an idealized, magical image of THE SUBJECT living their best life as this identity.

THE SUBJECT: The person shown in the reference photos. 
- Study their face carefully: bone structure, eyes, nose, mouth, skin tone, hair
- The output image MUST show this EXACT person - they must be immediately recognizable
- Do NOT create a different person or blend features

IDENTITY TO VISUALIZE:
{identity_context}

=== THIS IS A DREAM, NOT A DOCUMENTARY ===

This image should feel MAGICAL and IDEALIZED - like a movie poster for the best version of their life.
This is NOT a candid photo. This is NOT realistic documentary photography.
This is a VISUALIZATION OF A DREAM - aspirational, inspiring, and perfect.

CRITICAL - FACE IDENTITY:
- The face in the output MUST be 100% THE SUBJECT from the reference photos
- If someone who knows THE SUBJECT saw this image, they would immediately recognize them
- Do NOT generate a generic face or blend with other faces

Remember: This is a DREAM VISUALIZATION. Make them look like the hero of their own story.
The face must be THE EXACT PERSON from the reference photos, looking proud and masterful.
"""


# ============================================================================
# GENERATION
# ============================================================================

def generate_identity_image(client: genai.Client, output_name: str | None = None) -> tuple[str, Image.Image | None]:
    """
    Generate an identity image using character reference images.
    
    Args:
        client: Gemini API client
        output_name: Optional custom name for the output file (without extension)
    
    Returns:
        Tuple of (output_path, PIL Image or None if failed)
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Determine output path
    if output_name:
        output_path = f"{OUTPUT_DIR}/{output_name}.png"
    else:
        run_num = get_next_run_number()
        output_path = f"{OUTPUT_DIR}/{run_num:02d}.png"
    
    print("=" * 60)
    print("GENERATING IDENTITY IMAGE (DIRECT APPROACH)")
    print("=" * 60)
    print(f"Identity: {IDENTITY_NAME}")
    print(f"Reference images: {len(CHARACTER_VIEW_IMAGES)}")
    for img_path in CHARACTER_VIEW_IMAGES:
        print(f"  - {img_path}")
    print(f"Output: {output_path}")
    print()
    
    # Load character reference images
    reference_images = []
    for ref_path in CHARACTER_VIEW_IMAGES:
        if os.path.exists(ref_path):
            reference_images.append(Image.open(ref_path))
            print(f"✓ Loaded reference: {ref_path}")
        else:
            print(f"⚠ Reference not found: {ref_path}")
    
    if not reference_images:
        print("ERROR: No character reference images found!")
        return output_path, None
    
    print()
    
    prompt = build_prompt()
    print("Prompt:")
    print("-" * 40)
    print(prompt)
    print("-" * 40)
    print()
    
    # Build contents: reference images first, then prompt
    # Per Gemini docs: up to 5 images of humans for character consistency
    contents = reference_images + [prompt]
    
    # Retry loop - keep trying until success
    attempt = 0
    start_time = time.time()
    while True:
        attempt += 1
        elapsed = time.time() - start_time
        try:
            print(f"Generating image (attempt {attempt}, elapsed: {elapsed:.0f}s)...")
            attempt_start = time.time()
            
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
            
            attempt_duration = time.time() - attempt_start
            print(f"   API responded in {attempt_duration:.1f}s")
            
            # Check if we got a valid response
            if not response.parts:
                print(f"   WARNING: Response has no parts")
                print(f"   Response object: {response}")
                time.sleep(RETRY_DELAY)
                continue
            
            for i, part in enumerate(response.parts):
                print(f"   Processing part {i+1}/{len(response.parts)}...")
                if getattr(part, 'thought', False):
                    print(f"      (thought - skipping)")
                    continue
                if part.text:
                    print(f"   [Model] {part.text}")
                if part.inline_data is not None:
                    print(f"   Found image data, saving...")
                    image = part.as_image()
                    image.save(output_path)
                    total_time = time.time() - start_time
                    print(f"\n✓ Saved: {output_path} (total time: {total_time:.1f}s)")
                    return output_path, image
            
            print(f"   WARNING: No image in response parts, retrying...")
            
        except Exception as e:
            error_str = str(e)
            error_type = type(e).__name__
            is_retryable = "503" in error_str or "UNAVAILABLE" in error_str or "overloaded" in error_str.lower()
            
            if is_retryable:
                print(f"⚠ Attempt {attempt} failed - retrying in {RETRY_DELAY}s...")
                print(f"   Error type: {error_type}")
                print(f"   Message: {error_str[:200]}{'...' if len(error_str) > 200 else ''}")
                time.sleep(RETRY_DELAY)
            else:
                print(f"✗ Failed with non-retryable error:")
                print(f"   Error type: {error_type}")
                print(f"   Full message: {error_str}")
                return output_path, None


# ============================================================================
# MAIN
# ============================================================================

def main():
    # Parse arguments
    output_name = None
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_name = sys.argv[idx + 1]
    
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python generate_identity_image.py [--output <name>]")
        print()
        print("Generates an identity image directly using character reference images.")
        print("This uses Gemini's character consistency feature to place the subject")
        print("from the reference photos into an identity scene.")
        print()
        print("Options:")
        print("  --output <name>  Custom name for output file (default: numbered 01, 02, etc.)")
        print()
        print("Examples:")
        print("  python generate_identity_image.py")
        print("  python generate_identity_image.py --output conductor_01")
        print()
        print("Configure the identity by editing the constants at the top of the script:")
        print("  - IDENTITY_NAME, IDENTITY_CATEGORY, IDENTITY_VISUALIZATION")
        print("  - CHARACTER_VIEW_IMAGES (reference photos of the subject)")
        sys.exit(0)
    
    # Initialize client
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Generate the image
    output_path, image = generate_identity_image(client, output_name)
    
    # Summary
    print()
    print("=" * 60)
    print("COMPLETE")
    print("=" * 60)
    if image:
        print(f"Generated: {output_path}")
    else:
        print("Failed to generate image")


if __name__ == "__main__":
    main()
