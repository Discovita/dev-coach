"""
Generate Generic Identity Image Script

This script generates a cinematic, movie-poster quality identity image
with a GENERIC face (not the user's face). The face will be replaced
in a subsequent step.

This is Step 2 of the Identity Image Pipeline:
1. Generate Character Views (generate_character_views.py)
2. Generate Generic Identity Image (this script) <-- YOU ARE HERE
3. Generate Matched Character View
4. Merge/Face Swap

Usage:
    python generate_generic_identity_image.py [--output <directory>]

Examples:
    python generate_generic_identity_image.py
    python generate_generic_identity_image.py --output conductor_01

Output:
    Default: server/services/gemini/images/generic_identity/01.png
    With --output: server/services/gemini/images/generic_identity/<name>.png
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

OUTPUT_DIR = "server/services/gemini/images/generic_identity"

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
RESOLUTION = "4K"

# ============================================================================
# BODY DESCRIPTION CONSTANTS
# These describe the generic person in the image (face will be replaced later)
# ============================================================================

# Gender options: "man", "woman", "person" (gender neutral)
GENDER = "man"

# Height options: "short", "below average height", "average height", "above average height", "tall"
HEIGHT = "average height"

# Build options: "slim", "athletic", "average build", "stocky", "large"
BUILD = "athletic"

# Skin tone / ethnicity options: "light-skinned", "medium-skinned", "dark-skinned", 
# Or more specific: "Caucasian", "Asian", "Hispanic", "African American", "Middle Eastern", "South Asian"
ETHNICITY = "Caucasian"

# Age range: "young adult", "in their 30s", "middle-aged", "mature"
AGE = "in their 30s"

# Hair: "short brown hair", "long blonde hair", "bald", "gray hair", etc.
HAIR = "short brown hair"

# ============================================================================
# IDENTITY CONSTANTS
# These define what identity/role the person is visualized as
# ============================================================================

# Identity Name: The name of the identity being visualized
IDENTITY_NAME = "Conductor"

# Category: The identity category (e.g., "Passions & Talents", "Career & Purpose", etc.)
IDENTITY_CATEGORY = "Doer of Things"

# I Am Statement: Optional - the "I Am" statement for this identity
IDENTITY_I_AM_STATEMENT = "I am a conductor who leads with passion and precision"

# Visualization: Optional - the visualization/scene description for this identity
IDENTITY_VISUALIZATION = "Standing on a conductor's podium in a grand concert hall, arms raised dramatically with baton in hand, orchestra before me, audience applauding"

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


def get_body_description() -> str:
    """Build the body description from individual constants."""
    return f"a {HEIGHT} {BUILD} {ETHNICITY} {GENDER} {AGE} with {HAIR}"


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
    Build the prompt for generating a generic identity image.
    
    The key points:
    - Movie poster quality aesthetic
    - Cinematic, dramatic lighting
    - The face can be anyone (it will be replaced)
    - Focus on scene, body, pose, clothing, environment
    """
    body_description = get_body_description()
    identity_context = get_identity_context()
    
    return f"""We're creating a generic Identity Image for {body_description}.

Create a confident and inspiring image for this Identity.
The image should be a magical ideal visualization of them living as this Identity.

STYLE REQUIREMENTS:
- Idealized and aspirational - NOT a candid documentary photo
- Nothing negative - this is an inspiring, aspirational image

FRAMING REQUIREMENTS (CRITICAL - MUST FOLLOW):
- CLOSE-UP PORTRAIT FRAMING ONLY - chest-up or head-and-shoulders shot
- The face MUST occupy at least 15-20% of the total image area
- Frame as if taking a professional headshot or LinkedIn photo
- Camera should be CLOSE to the subject - within 3-4 feet
- DO NOT show anything below the chest/upper torso
- DO NOT use wide shots, establishing shots, or full-body framing
- DO NOT show legs, knees, or even the waist
- The face is the HERO of this image - it must be large and prominent
- Think "portrait photography" not "scene photography"
- If in doubt, ZOOM IN CLOSER

{identity_context}

IMPORTANT: The head does not need to match any specific person. Generate any appropriate head for this body type.
The face will be replaced in a subsequent step, so the face must be LARGE and CLEAR for face-swapping to work.

DO NOT include any text, words, letters, or watermarks in the image.

FINAL REMINDER - FRAMING IS CRITICAL:
This image will be used for face replacement. The face MUST be large in the frame.
CLOSE-UP ONLY. Chest-up or head-and-shoulders. NO full body. NO waist-down. NO wide shots.
The face should be the dominant feature of the image.
"""


# ============================================================================
# GENERATION
# ============================================================================

def generate_generic_identity_image(client: genai.Client, output_name: str | None = None) -> tuple[str, Image.Image | None]:
    """
    Generate a generic identity image.
    
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
    print("GENERATING GENERIC IDENTITY IMAGE")
    print("=" * 60)
    print(f"Identity: {IDENTITY_NAME}")
    print(f"Body: {get_body_description()}")
    print(f"Output: {output_path}")
    print()
    
    prompt = build_prompt()
    print("Prompt:")
    print("-" * 40)
    print(prompt)
    print("-" * 40)
    print()
    
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
                contents=[prompt],
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
        print("Usage: python generate_generic_identity_image.py [--output <name>]")
        print()
        print("Generates a cinematic identity image with a generic face.")
        print("The face will be replaced in a subsequent step.")
        print()
        print("Options:")
        print("  --output <name>  Custom name for output file (default: numbered 01, 02, etc.)")
        print()
        print("Examples:")
        print("  python generate_generic_identity_image.py")
        print("  python generate_generic_identity_image.py --output conductor_01")
        print()
        print("Configure the identity by editing the constants at the top of the script:")
        print("  - IDENTITY_NAME, IDENTITY_CATEGORY, IDENTITY_VISUALIZATION")
        print("  - GENDER, HEIGHT, BUILD, ETHNICITY, AGE, HAIR")
        sys.exit(0)
    
    # Initialize client
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Generate the image
    output_path, image = generate_generic_identity_image(client, output_name)
    
    # Summary
    print()
    print("=" * 60)
    print("COMPLETE")
    print("=" * 60)
    if image:
        print(f"Generated: {output_path}")
        print()
        print("Next step: Use this image as input for Step 3 (Generate Matched Character View)")
    else:
        print("Failed to generate image")


if __name__ == "__main__":
    main()
