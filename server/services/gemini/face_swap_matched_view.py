"""
Face Swap with Matched Character View Script

This script uses a 4-step approach:
1. Generate character views from a single source photo (or reuse existing)
2. Generate a cinematic intermediate identity image
3. Generate a "matched" character view - same head position and lighting as the intermediate
4. Face swap using ONLY the matched view (single image swap)

The idea: Create a bridge image that matches everything except the face,
making the final swap much simpler.

Usage:
  python face_swap_matched_view.py <source_image>
  python face_swap_matched_view.py <source_image> --skip-views
  python face_swap_matched_view.py <source_image> --skip-views --intermediate <path>

Examples:
  python face_swap_matched_view.py server/services/gemini/images/reference/face_only/casey_01.png
  python face_swap_matched_view.py server/services/gemini/images/reference/face_only/casey_01.png --skip-views
  python face_swap_matched_view.py server/services/gemini/images/reference/face_only/casey_01.png --skip-views --intermediate server/services/gemini/images/face_swap/face_swap_intermediate_10.png
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
# DIRECTORIES
# ============================================================================

OUTPUT_DIR = "server/services/gemini/images/face_swap_matched"
CHARACTER_VIEWS_DIR = "server/services/gemini/images/character_views"

SHOW_THINKING = False

# ============================================================================
# IMAGE CONFIG
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
# CHARACTER VIEWS CONFIG
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
    """Build the prompt for generating a generic identity image."""
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
    """Generate multiple angle views of a person from a single reference photo."""
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
"""
        
        try:
            response = client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=[prompt, source_image],
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                    image_config=types.ImageConfig(aspect_ratio="1:1", image_size="2K"),
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
    """Generate a generic identity image (cinematic, movie-poster quality)."""
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
    
    final_image = None
    intermediate_path = f"{OUTPUT_DIR}/intermediate_{run_num:02d}.png"
    
    for part in response.parts:
        if getattr(part, 'thought', False):
            continue
        if part.inline_data is not None:
            final_image = part.as_image()
            final_image.save(intermediate_path)
            print(f"Saved intermediate image: {intermediate_path}")
    
    if final_image is None:
        print("ERROR: Failed to generate generic identity image")
        sys.exit(1)
    
    return Image.open(intermediate_path), intermediate_path


# ============================================================================
# STEP 3: Generate Matched Character View
# ============================================================================

def generate_matched_character_view(
    intermediate_image: Image.Image,
    character_view_paths: list[str],
    run_num: int
) -> tuple[Image.Image, str]:
    """
    Generate a character view that matches the head position and lighting
    of the intermediate image. This creates a "bridge" image for easier swapping.
    """
    print()
    print("=" * 60)
    print("STEP 3: GENERATING MATCHED CHARACTER VIEW")
    print("=" * 60)
    print("Creating a character view that matches the intermediate image's")
    print("head position, angle, and lighting...")
    print()
    
    # Load all character views as reference for the person's face
    reference_images = []
    for ref_path in character_view_paths:
        if os.path.exists(ref_path):
            reference_images.append(Image.open(ref_path))
            print(f"  Loaded reference: {ref_path}")
    
    if not reference_images:
        print("ERROR: No character view images found!")
        sys.exit(1)
    
    print()
    
    matched_path = f"{OUTPUT_DIR}/matched_view_{run_num:02d}.png"
    
    prompt = """Look at the FIRST IMAGE (the scene image). Study the person in it carefully:
- What direction is their head facing?
- What angle is their head tilted?
- What is the lighting like on their face?
- What is the overall color grading and atmosphere?

Now, using the REMAINING IMAGES (the reference headshots), create a NEW headshot of that person that:

1. HEAD POSITION: The head must be in the EXACT same position and angle as the person in the scene image
   - Same direction the face is pointing
   - Same tilt of the head
   - Same turn of the neck
   
2. LIGHTING: Match the lighting from the scene image
   - Same direction of light source
   - Same warmth/coolness of light
   - Same shadow placement on the face
   - Same overall color grading

3. FACE: The face must be the person from the reference headshots
   - Same facial features, eyes, nose, mouth, jawline
   - Same skin tone and hair

The goal is to create a headshot that could seamlessly replace the face in the scene image.
Output just the head and shoulders, cropped similar to the reference headshots.

DO NOT include any text in the image.
"""

    # Contents: scene image first, then reference headshots, then prompt
    contents = [intermediate_image] + reference_images + [prompt]
    
    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="1:1", image_size="2K"),
        ),
    )
    
    matched_image = None
    for part in response.parts:
        if getattr(part, 'thought', False):
            continue
        if part.text:
            print(f"Response: {part.text}")
        if part.inline_data is not None:
            matched_image = part.as_image()
            matched_image.save(matched_path)
            print(f"Saved matched character view: {matched_path}")
    
    if matched_image is None:
        print("ERROR: Failed to generate matched character view")
        sys.exit(1)
    
    return Image.open(matched_path), matched_path


# ============================================================================
# STEP 4: Face Swap with Single Matched View
# ============================================================================

def face_swap_single(
    intermediate_image: Image.Image,
    matched_view_image: Image.Image,
    run_num: int
) -> Image.Image:
    """
    Swap the face using ONLY the single matched character view.
    Since the head position and lighting already match, this should be simpler.
    """
    print()
    print("=" * 60)
    print("STEP 4: FACE SWAP WITH MATCHED VIEW")
    print("=" * 60)
    print("Swapping face using the matched character view...")
    print()
    
    final_path = f"{OUTPUT_DIR}/final_{run_num:02d}.png"
    
    prompt = """Replace the face in the FIRST IMAGE with the face from the SECOND IMAGE.

The second image has been specifically created to match:
- The exact head position and angle
- The lighting direction and color
- The overall atmosphere

Your task is simple: Take the facial features (eyes, nose, mouth, skin texture, facial structure) from the second image and apply them to the person in the first image.

KEEP EVERYTHING ELSE THE SAME:
- Same body position and pose
- Same clothing
- Same background and environment
- Same overall composition

The head position should NOT change - only the facial features themselves.

Output a single edited image.
"""

    contents = [intermediate_image, matched_view_image, prompt]
    
    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(aspect_ratio=ASPECT_RATIO, image_size=RESOLUTION),
        ),
    )
    
    final_image = None
    for part in response.parts:
        if getattr(part, 'thought', False):
            continue
        if part.text:
            print(f"Response: {part.text}")
        if part.inline_data is not None:
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
    
    intermediate_path = None
    if "--intermediate" in sys.argv:
        idx = sys.argv.index("--intermediate")
        if idx + 1 < len(sys.argv):
            intermediate_path = sys.argv[idx + 1]
    
    args = [a for a in sys.argv[1:] if not a.startswith("--") and a != intermediate_path]
    
    if len(args) < 1:
        print("Usage: python face_swap_matched_view.py <source_image> [--skip-views] [--intermediate <path>]")
        print()
        print("4-step approach:")
        print("  1. Generate character views from source photo")
        print("  2. Generate cinematic intermediate identity image")
        print("  3. Generate matched character view (same head position/lighting as intermediate)")
        print("  4. Face swap using only the matched view")
        print()
        print("Options:")
        print("  --skip-views           Reuse existing character views")
        print("  --intermediate <path>  Use provided intermediate image")
        print()
        print("Examples:")
        print("  python face_swap_matched_view.py server/services/gemini/images/reference/face_only/casey_01.png")
        print("  python face_swap_matched_view.py server/services/gemini/images/reference/face_only/casey_01.png --skip-views --intermediate server/services/gemini/images/face_swap/face_swap_intermediate_10.png")
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
    print("FACE SWAP WITH MATCHED CHARACTER VIEW")
    print("=" * 60)
    print(f"Run number: {run_num:02d}")
    print(f"Source photo: {source_image_path}")
    print(f"Identity: {IDENTITY_NAME}")
    print()
    
    # Step 1: Character views
    if skip_views:
        character_view_paths = get_existing_character_views(source_basename)
        if not character_view_paths:
            print("ERROR: --skip-views specified but no existing character views found")
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
    
    # Step 2: Intermediate image
    if intermediate_path:
        if not os.path.exists(intermediate_path):
            print(f"ERROR: Intermediate image not found: {intermediate_path}")
            sys.exit(1)
        print(f"Using provided intermediate image: {intermediate_path}")
        intermediate_image = Image.open(intermediate_path)
        intermediate_save_path = f"{OUTPUT_DIR}/intermediate_{run_num:02d}.png"
        intermediate_image.save(intermediate_save_path)
        print(f"Saved copy as: {intermediate_save_path}")
        intermediate_image = Image.open(intermediate_save_path)
    else:
        intermediate_image, _ = generate_generic_identity(run_num)
    
    # Step 3: Matched character view
    matched_image, matched_path = generate_matched_character_view(
        intermediate_image, 
        character_view_paths, 
        run_num
    )
    
    # Step 4: Face swap with single matched view
    final_image = face_swap_single(intermediate_image, matched_image, run_num)
    
    # Summary
    print()
    print("=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print(f"Character views: {CHARACTER_VIEWS_DIR}/{source_basename}_*.png")
    print(f"Intermediate image: {OUTPUT_DIR}/intermediate_{run_num:02d}.png")
    print(f"Matched character view: {OUTPUT_DIR}/matched_view_{run_num:02d}.png")
    print(f"Final image: {OUTPUT_DIR}/final_{run_num:02d}.png")
