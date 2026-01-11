"""
Face Swap with Character Views Script

This script combines:
1. Generate character views from a single source photo (or reuse existing)
2. Generate a generic identity image (cinematic, movie-poster quality)
3. Face swap using the character views as reference images

Usage:
  python face_swap_character_views.py <source_image>               # Generate views + intermediate + face swap
  python face_swap_character_views.py <source_image> --skip-views  # Reuse existing views + intermediate + face swap
  python face_swap_character_views.py <source_image> --skip-views --intermediate <path>  # Reuse views + provided intermediate + face swap

Examples:
  python face_swap_character_views.py server/services/gemini/images/reference/face_only/casey_01.png
  python face_swap_character_views.py server/services/gemini/images/reference/face_only/casey_01.png --skip-views
  python face_swap_character_views.py server/services/gemini/images/reference/face_only/casey_01.png --skip-views --intermediate server/services/gemini/images/face_swap/face_swap_intermediate_10.png
"""

import sys
import re
import glob
from google import genai
from pathlib import Path
from dotenv import load_dotenv
import os
from PIL import Image
from google.genai import types

# Load environment variables from server/.env
script_path = Path(__file__).resolve()
current = script_path.parent
while current != current.parent:
    if current.name == "server":
        load_dotenv(current / ".env")
        break
    current = current.parent

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ============================================================================
# DIRECTORIES - Same as generate_identity_image.py
# ============================================================================

OUTPUT_DIR = "server/services/gemini/images/face_swap_cv"
CHARACTER_VIEWS_DIR = "server/services/gemini/images/character_views"

# Whether to show thinking process
SHOW_THINKING = False

# ============================================================================
# IMAGE CONFIG CONSTANTS
# ============================================================================

ASPECT_RATIO = "16:9"
RESOLUTION = "4K"

# ============================================================================
# BODY DESCRIPTION CONSTANTS
# ============================================================================

GENDER = "man"
HEIGHT = "average height"
BUILD = "athletic"
ETHNICITY = "Caucasian"
AGE = "in their 30s"
HAIR = "short brown hair"

# ============================================================================
# IDENTITY CONSTANTS
# ============================================================================

IDENTITY_NAME = "Conductor"
IDENTITY_CATEGORY = "Passions & Talents"
IDENTITY_I_AM_STATEMENT = None
IDENTITY_VISUALIZATION = None
IDENTITY_NOTES = None

# ============================================================================
# CHARACTER VIEWS CONFIG - Same as generate_identity_image.py
# ============================================================================

VIEWS_TO_GENERATE = [
    ("front", "looking directly at the camera, face pointed straight ahead", "camera directly in front"),
    ("profile_left", "in a TRUE SIDE PROFILE view - the camera is positioned at exactly 90 degrees to the left side of their face, showing only the left side of their face with the nose pointing to the right edge of the frame", "camera at 90 degrees to their left"),
    ("profile_right", "in a TRUE SIDE PROFILE view - the camera is positioned at exactly 90 degrees to the right side of their face, showing only the right side of their face with the nose pointing to the left edge of the frame", "camera at 90 degrees to their right"),
    ("three_quarter_left", "at a 45-degree angle with the camera to their left - their face is turned slightly to their right so we see more of their left cheek, left ear visible", "camera at 45 degrees to their left"),
    ("three_quarter_right", "at a 45-degree angle with the camera to their right - their face is turned slightly to their left so we see more of their right cheek, right ear visible", "camera at 45 degrees to their right"),
]

# ============================================================================
# PROMPTS
# ============================================================================

def get_identity_context() -> str:
    """Format identity context for the prompt."""
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


def get_generic_identity_prompt() -> str:
    """
    Build the prompt for generating a generic identity image.
    This generates the cinematic, movie-poster quality image.
    The face doesn't matter - we'll swap it in step 3.
    """
    body_description = f"a {HEIGHT} {BUILD} {ETHNICITY} {GENDER} {AGE} with {HAIR}"
    identity_context = get_identity_context()
    
    return f"""We're creating a generic Identity Image for a {body_description}.

Create a professional, confident, and inspiring image for this Identity.
The image should be an ideal visualization of them living as this Identity.
Give it a movie poster quality aesthetic.
Nothing negative should be conveyed - this is an aspirational image.

{identity_context}

IMPORTANT: The face does not need to match any specific person. Generate any appropriate face for this body type.
Focus on getting the body proportions, clothing, pose, and environment correct.
The face will be replaced in a subsequent step, so focus on the scene, body, and overall composition.

DO NOT include any text, words, letters, or watermarks in the image. The image should be purely visual with no text elements.
"""


FACE_SWAP_PROMPT = """Edit the first image to show the person from the reference headshots instead.

CRITICAL - The output must be IDENTICAL to the first image EXCEPT for the facial features:
- SAME exact head position and angle (do NOT change where the head is looking)
- SAME exact body position and pose
- SAME exact clothing
- SAME exact background and environment
- SAME exact lighting and color grading
- SAME exact composition and framing

The ONLY change should be the facial features themselves. Study the reference headshots and apply those facial features (face shape, eyes, nose, mouth, jawline, skin tone) to the person in the scene, but keep the head turned the same direction as the original.

If the person in the first image is looking to the left, the output must also be looking to the left.
If the person in the first image is looking up, the output must also be looking up.
Do NOT make the person look at the camera unless they already are in the first image.

Output a single edited image.
"""

# ============================================================================
# UTILITIES
# ============================================================================

def get_next_run_number() -> int:
    """Find the next available number for outputs."""
    pattern = f"{OUTPUT_DIR}/final_*.png"
    existing_files = glob.glob(pattern)
    
    if not existing_files:
        return 1
    
    numbers = []
    for f in existing_files:
        match = re.search(r'final_(\d+)\.png', f)
        if match:
            numbers.append(int(match.group(1)))
    
    return max(numbers) + 1 if numbers else 1


def get_existing_character_views(source_basename: str) -> list[str]:
    """Check if character views already exist for this source image."""
    existing_paths = []
    for view_suffix, _, _ in VIEWS_TO_GENERATE:
        path = f"{CHARACTER_VIEWS_DIR}/{source_basename}_{view_suffix}.png"
        if os.path.exists(path):
            existing_paths.append(path)
    return existing_paths


# ============================================================================
# STEP 1: Generate Character Views
# ============================================================================

def generate_character_views(source_path: str) -> list[str]:
    """
    Generate multiple angle views of a person from a single reference photo.
    Returns list of generated image paths.
    """
    os.makedirs(CHARACTER_VIEWS_DIR, exist_ok=True)
    
    source_basename = os.path.splitext(os.path.basename(source_path))[0]
    source_image = Image.open(source_path)
    
    print("=" * 60)
    print("STEP 1: GENERATING CHARACTER VIEWS")
    print("=" * 60)
    print(f"Source: {source_path}")
    print()
    
    generated_paths = []
    
    for view_suffix, view_description, camera_hint in VIEWS_TO_GENERATE:
        output_path = f"{CHARACTER_VIEWS_DIR}/{source_basename}_{view_suffix}.png"
        print(f"Generating: {view_suffix}...")
        
        prompt = f"""A professional studio headshot portrait of this person against a plain white background, {view_description}.

Camera position: {camera_hint}

Keep the person's face EXACTLY the same - same facial features, same eyes, same nose, same mouth, same skin tone, same hair style and color. 
This must be recognizably the same person, just from a different angle.

IMPORTANT - Professional retouching requirements:
- Smooth, flawless skin - minimize visible pores, blemishes, and imperfections
- This should look like a professionally retouched headshot photo
- Clean, polished appearance like a corporate or modeling headshot
- Soft, even studio lighting

DO NOT change any facial features. DO NOT add or remove facial hair. DO NOT change the hairstyle.
The image should look like it was taken by a professional photographer with professional retouching applied.
"""
        
        try:
            response = client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=[prompt, source_image],
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
                    break
        except Exception as e:
            print(f"  ✗ Failed: {e}")
        
        print()
    
    return generated_paths


# ============================================================================
# STEP 2: Generate Generic Identity Image
# ============================================================================

def generate_generic_identity(run_num: int) -> tuple[Image.Image, str]:
    """
    Generate a generic identity image based on body description constants.
    The face doesn't matter - we're going to swap it out in step 3.
    """
    print("=" * 60)
    print("STEP 2: GENERATING GENERIC IDENTITY IMAGE")
    print("=" * 60)
    print(f"Body description: {GENDER}, {HEIGHT}, {BUILD}, {ETHNICITY}, {AGE}, {HAIR}")
    print()
    
    prompt = get_generic_identity_prompt()
    print(f"Prompt:\n{prompt}\n")
    
    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(aspect_ratio=ASPECT_RATIO, image_size=RESOLUTION),
        ),
    )
    
    # Process response
    thinking_count = 0
    final_image = None
    intermediate_path = f"{OUTPUT_DIR}/intermediate_{run_num:02d}.png"
    
    for part in response.parts:
        is_thinking = getattr(part, 'thought', False)
        
        if is_thinking:
            if SHOW_THINKING:
                if part.text is not None:
                    print(f"  [THINKING] {part.text}")
                elif part.inline_data is not None:
                    thinking_count += 1
        else:
            if part.text is not None:
                print(f"Response: {part.text}")
            elif part.inline_data is not None:
                final_image = part.as_image()
                final_image.save(intermediate_path)
                print(f"Saved intermediate image: {intermediate_path}")
    
    if final_image is None:
        print("ERROR: Failed to generate generic identity image")
        sys.exit(1)
    
    return Image.open(intermediate_path), intermediate_path


# ============================================================================
# STEP 3: Face Swap
# ============================================================================

def face_swap(intermediate_image: Image.Image, character_view_paths: list[str], run_num: int) -> Image.Image:
    """
    Swap the face in the intermediate image with the user's face from character views.
    """
    print()
    print("=" * 60)
    print("STEP 3: FACE SWAP")
    print("=" * 60)
    print(f"Using {len(character_view_paths)} character view images")
    print()
    
    # Load character view images
    reference_images = []
    for ref_path in character_view_paths:
        if os.path.exists(ref_path):
            reference_images.append(Image.open(ref_path))
            print(f"  Loaded: {ref_path}")
        else:
            print(f"  WARNING: Character view not found: {ref_path}")
    
    if not reference_images:
        print("ERROR: No character view images found!")
        sys.exit(1)
    
    print()
    
    # Build content list: reference faces first, then scene, then instruction
    contents = reference_images + [intermediate_image, FACE_SWAP_PROMPT]
    
    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(aspect_ratio=ASPECT_RATIO, image_size=RESOLUTION),
        ),
    )
    
    # Process response
    final_image = None
    final_path = f"{OUTPUT_DIR}/final_{run_num:02d}.png"
    
    for part in response.parts:
        is_thinking = getattr(part, 'thought', False)
        
        if is_thinking:
            continue
        else:
            if part.text is not None:
                print(f"Response: {part.text}")
            elif part.inline_data is not None:
                final_image = part.as_image()
                final_image.save(final_path)
                print(f"Saved final image: {final_path}")
    
    if final_image is None:
        print("ERROR: Failed to perform face swap")
        sys.exit(1)
    
    return final_image


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Parse arguments
    skip_views = "--skip-views" in sys.argv
    
    # Check for --intermediate flag
    intermediate_path = None
    if "--intermediate" in sys.argv:
        idx = sys.argv.index("--intermediate")
        if idx + 1 < len(sys.argv):
            intermediate_path = sys.argv[idx + 1]
    
    # Get source image (first non-flag argument)
    args = [a for a in sys.argv[1:] if not a.startswith("--") and a != intermediate_path]
    
    if len(args) < 1:
        print("Usage: python face_swap_character_views.py <source_image> [--skip-views] [--intermediate <path>]")
        print()
        print("Options:")
        print("  --skip-views           Skip character view generation, reuse existing")
        print("  --intermediate <path>  Use provided intermediate image instead of generating new")
        print()
        print("Examples:")
        print("  python face_swap_character_views.py server/services/gemini/images/reference/face_only/casey_01.png")
        print("  python face_swap_character_views.py server/services/gemini/images/reference/face_only/casey_01.png --skip-views")
        print("  python face_swap_character_views.py server/services/gemini/images/reference/face_only/casey_01.png --skip-views --intermediate server/services/gemini/images/face_swap/face_swap_intermediate_10.png")
        sys.exit(1)
    
    source_image_path = args[0]
    
    if not os.path.exists(source_image_path):
        print(f"ERROR: Source image not found: {source_image_path}")
        sys.exit(1)
    
    source_basename = os.path.splitext(os.path.basename(source_image_path))[0]
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Get run number
    run_num = get_next_run_number()
    
    print("=" * 60)
    print("FACE SWAP WITH CHARACTER VIEWS")
    print("=" * 60)
    print(f"Run number: {run_num:02d}")
    print(f"Source photo: {source_image_path}")
    print(f"Identity: {IDENTITY_NAME}")
    print()
    
    # Step 1: Generate or reuse character views
    if skip_views:
        character_view_paths = get_existing_character_views(source_basename)
        if not character_view_paths:
            print("ERROR: --skip-views specified but no existing character views found")
            print(f"Expected files in: {CHARACTER_VIEWS_DIR}/{source_basename}_*.png")
            sys.exit(1)
        print(f"Skipping character view generation, using {len(character_view_paths)} existing views")
        for p in character_view_paths:
            print(f"  - {p}")
        print()
    else:
        character_view_paths = generate_character_views(source_image_path)
        if not character_view_paths:
            print("ERROR: Failed to generate any character views")
            sys.exit(1)
    
    # Step 2: Generate or use provided intermediate image
    if intermediate_path:
        if not os.path.exists(intermediate_path):
            print(f"ERROR: Intermediate image not found: {intermediate_path}")
            sys.exit(1)
        print(f"Using provided intermediate image: {intermediate_path}")
        intermediate_image = Image.open(intermediate_path)
        # Save a copy
        intermediate_save_path = f"{OUTPUT_DIR}/intermediate_{run_num:02d}.png"
        intermediate_image.save(intermediate_save_path)
        print(f"Saved copy as: {intermediate_save_path}")
    else:
        intermediate_image, _ = generate_generic_identity(run_num)
    
    # Step 3: Face swap
    final_image = face_swap(intermediate_image, character_view_paths, run_num)
    
    # Summary
    print()
    print("=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print(f"Character views: {CHARACTER_VIEWS_DIR}/{source_basename}_*.png")
    print(f"Intermediate image: {OUTPUT_DIR}/intermediate_{run_num:02d}.png")
    print(f"Final image: {OUTPUT_DIR}/final_{run_num:02d}.png")
