"""
Generate Character Views Script

This script takes one or more user photos and generates 5 clean, professional
headshot views at different angles:
- Front (looking directly at camera)
- Profile Left (true 90-degree side profile)
- Profile Right (true 90-degree side profile)
- Three-Quarter Left (45-degree angle)
- Three-Quarter Right (45-degree angle)

This creates a quality baseline from potentially low-quality user uploads,
which can then be used as reference images for character consistency.

Usage:
    python generate_character_views.py <source_image> [source_image2 ...] [--output <directory>]

Examples:
    # Single image
    python generate_character_views.py server/services/gemini/images/reference/face_only/casey_01.png
    
    # Multiple images for better character consistency
    python generate_character_views.py img1.png img2.png img3.png --output casey
    
Output:
    Default: Character views saved to server/services/gemini/images/character_views/01/
    With --output: Character views saved to server/services/gemini/images/character_views/<name>/
"""

import os
import sys
import glob
import shutil
import time
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
from google import genai
from google.genai import types

# ============================================================================
# RETRY CONFIGURATION
# ============================================================================

MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 5  # seconds
RETRY_BACKOFF_MULTIPLIER = 2  # exponential backoff

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

CHARACTER_VIEWS_DIR = "server/services/gemini/images/character_views"

# ============================================================================
# USER APPEARANCE CONSTANTS
# These will eventually come from user input during onboarding
# ============================================================================

# Gender: "man", "woman"
GENDER = "man"

# Ethnicity: "Caucasian", "Asian", "Hispanic", "African American", "Middle Eastern", "South Asian", etc.
ETHNICITY = "Caucasian"

# Hair color: "brown", "black", "blonde", "red", "gray", "white", "auburn", etc.
HAIR_COLOR = "brown"

# Eye color: "brown", "blue", "green", "hazel", "gray", "amber", etc.
EYE_COLOR = "brown"


def get_clothing_description() -> str:
    """Get the clothing description based on gender."""
    if GENDER == "woman":
        return "a light blue blouse"
    else:
        return "a light blue collared shirt"


# ============================================================================
# UTILITIES
# ============================================================================

def get_next_run_number() -> int:
    """Find the next available numbered directory."""
    if not os.path.exists(CHARACTER_VIEWS_DIR):
        return 1
    
    # Look for existing numbered directories (01, 02, 03, etc.)
    existing_dirs = glob.glob(f"{CHARACTER_VIEWS_DIR}/[0-9][0-9]")
    
    if not existing_dirs:
        return 1
    
    numbers = []
    for d in existing_dirs:
        dirname = os.path.basename(d)
        try:
            numbers.append(int(dirname))
        except ValueError:
            continue
    
    return max(numbers) + 1 if numbers else 1

# ============================================================================
# FRAMING REQUIREMENTS (for consistent distance/cropping)
# ============================================================================

FRAMING_REQUIREMENTS = """
FRAMING (CRITICAL - must be consistent across all views):
- Head and shoulders shot - crop from mid-chest up
- Face should fill approximately 40-50% of the frame height
- Top of head should have about 10-15% padding from top edge
- Shoulders should be visible but cropped at mid-chest
- Face should be centered horizontally in the frame
- Same apparent distance from camera in every shot
"""

# ============================================================================
# VIEW DEFINITIONS
# All directions are described from the VIEWER'S PERSPECTIVE (what you see in the final image)
# We use "left side of frame" and "right side of frame" to avoid confusion
# ============================================================================

VIEWS_TO_GENERATE = [
    (
        "front",
        """FRONT VIEW - Face centered, looking directly at camera.
        
        EXPRESSION: Natural, warm SMILE with teeth showing. Friendly and approachable.
        
        IN THE FINAL IMAGE:
        - Face is perfectly centered, symmetrical
        - Both eyes equally visible, looking at camera
        - Nose points straight at the viewer
        - Both ears equally visible (or equally hidden)
        - Both shoulders visible and level
        - Smiling with teeth visible"""
    ),
    (
        "profile_left",
        """TRUE SIDE PROFILE - Nose pointing to the RIGHT side of the frame.
        
        EXPRESSION: Neutral, relaxed. Mouth closed, lips together naturally.
        
        Think of a coin portrait or silhouette cutout.
        
        IN THE FINAL IMAGE:
        - The nose points toward the RIGHT edge of the image
        - Only ONE eye is visible (no part of the second eye should be seen)
        - ONE ear is visible on the LEFT side of the head
        - The back/rear of the head is on the LEFT side of the frame
        - The face/nose is on the RIGHT side of the frame
        - You should see the profile outline: forehead, nose, lips, chin
        
        THIS IS NOT A 3/4 VIEW. If you can see any part of the second eye, it's wrong."""
    ),
    (
        "profile_right",
        """TRUE SIDE PROFILE - Nose pointing to the LEFT side of the frame.
        
        EXPRESSION: Neutral, relaxed. Mouth closed, lips together naturally.
        
        Think of a coin portrait or silhouette cutout.
        
        IN THE FINAL IMAGE:
        - The nose points toward the LEFT edge of the image
        - Only ONE eye is visible (no part of the second eye should be seen)
        - ONE ear is visible on the RIGHT side of the head
        - The back/rear of the head is on the RIGHT side of the frame
        - The face/nose is on the LEFT side of the frame
        - You should see the profile outline: forehead, nose, lips, chin
        
        THIS IS NOT A 3/4 VIEW. If you can see any part of the second eye, it's wrong."""
    ),
    (
        "three_quarter_left",
        """3/4 VIEW - Face angled, with nose pointing toward the RIGHT side of the frame.
        
        EXPRESSION: Natural, warm SMILE with teeth showing. Friendly and approachable.
        
        IN THE FINAL IMAGE:
        - BOTH eyes are visible, but the eye on the RIGHT side of the image is more prominent/closer
        - Nose is angled toward the RIGHT (but not full profile - you can still see both eyes)
        - The ear on the LEFT side of the image is fully visible
        - The ear on the RIGHT side of the image is hidden or barely visible
        - More of the cheek on the RIGHT side of the image is visible
        - The face is turned approximately 30-45 degrees from front
        - Smiling with teeth visible"""
    ),
    (
        "three_quarter_right",
        """3/4 VIEW - Face angled, with nose pointing toward the LEFT side of the frame.
        
        EXPRESSION: Neutral, relaxed. Mouth closed, lips together naturally.
        
        IN THE FINAL IMAGE:
        - BOTH eyes are visible, but the eye on the LEFT side of the image is more prominent/closer
        - Nose is angled toward the LEFT (but not full profile - you can still see both eyes)
        - The ear on the RIGHT side of the image is fully visible
        - The ear on the LEFT side of the image is hidden or barely visible
        - More of the cheek on the LEFT side of the image is visible
        - The face is turned approximately 30-45 degrees from front"""
    ),
]

# ============================================================================
# GENERATION
# ============================================================================

def generate_character_views(client: genai.Client, source_paths: list[str], output_name: str | None = None) -> tuple[str, list[str]]:
    """
    Generate multiple angle views of a person from one or more reference photos.
    
    Args:
        client: Gemini API client
        source_paths: List of paths to source images (1-5 images for character consistency)
        output_name: Optional name for the output directory. If None, uses numbered directories.
    
    Returns tuple of (output_directory, list of generated image paths).
    """
    # Determine output directory
    if output_name:
        output_dir = f"{CHARACTER_VIEWS_DIR}/{output_name}"
    else:
        run_num = get_next_run_number()
        output_dir = f"{CHARACTER_VIEWS_DIR}/{run_num:02d}"
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Load all source images
    source_images = []
    for i, source_path in enumerate(source_paths[:5]):  # Max 5 for character consistency
        source_images.append(Image.open(source_path))
        # Copy source images into the output directory for reference
        source_copy_path = f"{output_dir}/source_{i+1:02d}.png"
        shutil.copy(source_path, source_copy_path)
    
    print("=" * 60)
    print("GENERATING CHARACTER VIEWS")
    print("=" * 60)
    print(f"Source images: {len(source_images)}")
    for sp in source_paths[:5]:
        print(f"  - {sp}")
    print(f"Output directory: {output_dir}")
    print()
    
    generated_paths = []
    
    for view_suffix, view_description in VIEWS_TO_GENERATE:
        output_path = f"{output_dir}/{view_suffix}.png"
        print(f"Generating: {view_suffix}...")
        
        clothing = get_clothing_description()
        
        # Build prompt with reference to multiple images if provided
        if len(source_images) > 1:
            reference_note = f"Study all {len(source_images)} reference photos to understand this person's face from different angles."
        else:
            reference_note = "Study the reference photo carefully."
        
        prompt = f"""Create a professional studio headshot portrait of this {ETHNICITY} {GENDER} against a plain white background.

{reference_note}

{view_description}

{FRAMING_REQUIREMENTS}

CLOTHING: The person must be wearing {clothing}. This is required for consistency across all images.

Keep the person's face EXACTLY the same - same facial features, same eyes, same nose, same mouth, same skin tone, same hair style and color. 
This must be recognizably the same person, just from a different angle.

CRITICAL - Maintain these specific features:
- Gender: {GENDER}
- Ethnicity: {ETHNICITY}
- Hair color: {HAIR_COLOR} (DO NOT change the hair color)
- Eye color: {EYE_COLOR} (DO NOT change the eye color - this is very important)
- Clothing: {clothing} (same in every image)

IMPORTANT - Professional retouching requirements:
- Smooth, flawless skin - minimize visible pores, blemishes, and imperfections
- This should look like a professionally retouched headshot photo
- Clean, polished appearance like a corporate or modeling headshot
- Soft, even studio lighting
- Plain white background

DO NOT change any facial features. DO NOT add or remove facial hair. DO NOT change the hairstyle.
DO NOT change the eye color - eyes must be {EYE_COLOR}.
DO NOT change the hair color - hair must be {HAIR_COLOR}.
DO NOT change the clothing - must be {clothing}.
The image should look like it was taken by a professional photographer with professional retouching applied.
"""
        
        # Build contents array: prompt first, then all source images
        contents = [prompt] + source_images
        
        # Retry loop with exponential backoff
        retry_delay = INITIAL_RETRY_DELAY
        success = False
        
        for attempt in range(MAX_RETRIES):
            try:
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
                    if part.inline_data is not None:
                        image = part.as_image()
                        image.save(output_path)
                        print(f"  ✓ Saved: {output_path}")
                        generated_paths.append(output_path)
                        success = True
                        break
                
                if success:
                    break
                    
            except Exception as e:
                error_str = str(e)
                is_retryable = "503" in error_str or "UNAVAILABLE" in error_str or "overloaded" in error_str.lower()
                
                if is_retryable and attempt < MAX_RETRIES - 1:
                    print(f"  ⚠ Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
                    print(f"    Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= RETRY_BACKOFF_MULTIPLIER
                else:
                    print(f"  ✗ Failed after {attempt + 1} attempts: {e}")
        
        print()
    
    return output_dir, generated_paths


# ============================================================================
# MAIN
# ============================================================================

def main():
    # Parse arguments
    output_name = None
    args = sys.argv[1:]
    
    # Extract --output flag if present
    if "--output" in args:
        idx = args.index("--output")
        if idx + 1 < len(args):
            output_name = args[idx + 1]
            # Remove --output and its value
            args = args[:idx] + args[idx + 2:]
    
    # Remaining args are source image paths
    source_image_paths = args
    
    if len(source_image_paths) < 1:
        print("Usage: python generate_character_views.py <source_image> [source_image2 ...] [--output <directory_name>]")
        print()
        print("This script takes one or more user photos and generates 5 clean headshot views:")
        print("  - front (looking directly at camera)")
        print("  - profile_left (true 90-degree side profile)")
        print("  - profile_right (true 90-degree side profile)")
        print("  - three_quarter_left (45-degree angle)")
        print("  - three_quarter_right (45-degree angle)")
        print()
        print("Options:")
        print("  --output <name>  Custom name for output directory (default: numbered 01, 02, etc.)")
        print()
        print("Examples:")
        print("  # Single image")
        print("  python generate_character_views.py server/services/gemini/images/reference/face_only/casey_01.png")
        print()
        print("  # Multiple images for better character consistency")
        print("  python generate_character_views.py img1.png img2.png img3.png --output casey")
        sys.exit(1)
    
    # Validate all source images exist
    for source_image_path in source_image_paths:
        if not os.path.exists(source_image_path):
            print(f"ERROR: Source image not found: {source_image_path}")
            sys.exit(1)
    
    # Initialize client
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Generate character views
    output_dir, generated_paths = generate_character_views(client, source_image_paths, output_name)
    
    # Summary
    print()
    print("=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print(f"Output directory: {output_dir}")
    print(f"Generated {len(generated_paths)} character views:")
    for path in generated_paths:
        print(f"  - {path}")


if __name__ == "__main__":
    main()
