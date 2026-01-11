"""
Generate an identity image with character consistency.

This script takes a SINGLE user photo and:
1. Generates 5 clean, professional headshot views (front, profiles, 3/4 angles)
   - This creates a quality baseline from potentially low-quality user uploads
2. Uses those generated headshots as reference images for character consistency
3. Generates the final identity image showing the person in their identity role

Usage:
    python server/services/gemini/generate_identity_image.py <source_image>

Example:
    python server/services/gemini/generate_identity_image.py server/services/gemini/images/reference/face_only/casey_01.png

Output:
    - Character views saved to server/services/gemini/images/character_views/
    - Identity image saved to server/services/gemini/images/identity/
"""

import os
import sys
import glob
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
CHARACTER_VIEWS_DIR = "server/services/gemini/images/character_views"

# ============================================================================
# BODY DESCRIPTION CONSTANTS
# Toggle these to test different body types
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
# IDENTITY CONFIGURATION
# ============================================================================

IDENTITY_NAME = "Conductor"
IDENTITY_CATEGORY = "Passions & Talents"
IDENTITY_I_AM_STATEMENT = "I am a conductor who leads with passion and precision"
IDENTITY_VISUALIZATION = "Standing on a conductor's podium in a grand concert hall, arms raised dramatically with baton in hand, orchestra before me, audience applauding"

# ============================================================================
# IMAGE SETTINGS
# ============================================================================

ASPECT_RATIO = "16:9"
RESOLUTION = "2K"

# Headshot views to generate from the source photo
# Each tuple: (filename_suffix, angle_description, camera_position_hint)
VIEWS_TO_GENERATE = [
    ("front", "looking directly at the camera, face pointed straight ahead", "camera directly in front"),
    ("profile_left", "in a TRUE SIDE PROFILE view - the camera is positioned at exactly 90 degrees to the left side of their face, showing only the left side of their face with the nose pointing to the right edge of the frame", "camera at 90 degrees to their left"),
    ("profile_right", "in a TRUE SIDE PROFILE view - the camera is positioned at exactly 90 degrees to the right side of their face, showing only the right side of their face with the nose pointing to the left edge of the frame", "camera at 90 degrees to their right"),
    ("three_quarter_left", "at a 45-degree angle with the camera to their left - their face is turned slightly to their right so we see more of their left cheek, left ear visible", "camera at 45 degrees to their left"),
    ("three_quarter_right", "at a 45-degree angle with the camera to their right - their face is turned slightly to their left so we see more of their right cheek, right ear visible", "camera at 45 degrees to their right"),
]

# ============================================================================
# UTILITIES
# ============================================================================

def get_next_output_number() -> int:
    """Find the next available number for output files."""
    pattern = f"{OUTPUT_DIR}/identity_*.png"
    existing_files = glob.glob(pattern)
    
    if not existing_files:
        return 1
    
    numbers = []
    for f in existing_files:
        basename = os.path.basename(f)
        try:
            num = int(basename.replace("identity_", "").replace(".png", ""))
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
    Matches the format used in face_swap.py
    """
    parts = [
        f'Identity Name: "{IDENTITY_NAME}"',
        f"Category: {IDENTITY_CATEGORY}",
    ]
    
    if IDENTITY_I_AM_STATEMENT:
        parts.append(f"I Am Statement: {IDENTITY_I_AM_STATEMENT}")
    
    if IDENTITY_VISUALIZATION:
        parts.append(f"Visualization: {IDENTITY_VISUALIZATION}")
    
    return "\n".join(parts)


def build_identity_prompt() -> str:
    """
    Build the prompt for identity image generation.
    Uses the same prompt style from face_swap.py (which produces great images)
    but adds character consistency requirement for the reference photos.
    """
    body_description = get_body_description()
    identity_context = get_identity_context()
    
    prompt = f"""We're creating an artistic, cinematic Identity Image for a {body_description}.

STYLE REQUIREMENTS (CRITICAL - DO NOT IGNORE):
- Movie poster quality aesthetic with dramatic, cinematic lighting
- Golden hour or dramatic studio lighting with visible light rays
- Idealized, aspirational, NOT documentary or photojournalistic
- Think Hollywood movie poster, NOT a candid photo from a real event
- Warm, golden tones with dramatic atmosphere
- Professional, confident, and inspiring composition

{identity_context}

The person shown must have the face from the reference photos - same facial features, eyes, nose, mouth, jawline, skin tone, and hair. But the IMAGE STYLE must be cinematic and artistic, not realistic documentary photography.

DO NOT create a realistic photo that looks like it was taken at an actual event.
DO create an idealized, movie-poster quality visualization.

DO NOT include any text, words, letters, or watermarks in the image.
"""
    return prompt


# ============================================================================
# STEP 1: GENERATE CHARACTER VIEWS (optional)
# ============================================================================

def generate_character_views(client: genai.Client, source_path: str) -> list[str]:
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
# STEP 2: GENERATE IDENTITY IMAGE
# ============================================================================

def generate_identity_image(client: genai.Client, reference_paths: list[str]) -> str | None:
    """
    Generate an identity image using reference photos for character consistency.
    
    Returns the output path if successful, None otherwise.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    run_num = get_next_output_number()
    output_path = f"{OUTPUT_DIR}/identity_{run_num:02d}.png"
    
    print("=" * 60)
    print("STEP 2: GENERATING IDENTITY IMAGE")
    print("=" * 60)
    print(f"Run number: {run_num}")
    print(f"Identity: {IDENTITY_NAME}")
    print()
    
    # Load reference images
    print("Loading reference images...")
    reference_images = []
    for ref_path in reference_paths[:5]:  # Max 5 for character consistency
        if os.path.exists(ref_path):
            reference_images.append(Image.open(ref_path))
            print(f"  ✓ {ref_path}")
        else:
            print(f"  ✗ Not found: {ref_path}")
    
    if not reference_images:
        print("ERROR: No reference images loaded!")
        return None
    
    print(f"\nUsing {len(reference_images)} reference images")
    print()
    
    # Build prompt
    prompt = build_identity_prompt()
    print("Prompt:")
    print("-" * 40)
    print(prompt)
    print("-" * 40)
    print()
    
    # Contents: prompt first, then reference images (per docs)
    contents = [prompt] + reference_images
    
    print("Generating identity image...")
    
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
    
    # Process response
    for part in response.parts:
        if getattr(part, 'thought', False):
            continue
        if part.text:
            print(f"[Model] {part.text}")
        if part.inline_data is not None:
            image = part.as_image()
            image.save(output_path)
            print(f"\n✓ Saved: {output_path}")
            return output_path
    
    print("\nERROR: No image generated")
    return None


# ============================================================================
# MAIN
# ============================================================================

def get_existing_character_views(source_basename: str) -> list[str]:
    """Check if character views already exist for this source image."""
    existing_paths = []
    for view_suffix, _, _ in VIEWS_TO_GENERATE:
        path = f"{CHARACTER_VIEWS_DIR}/{source_basename}_{view_suffix}.png"
        if os.path.exists(path):
            existing_paths.append(path)
    return existing_paths


def main():
    # Parse arguments
    skip_views = "--skip-views" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--skip-views"]
    
    if len(args) < 1:
        print("Usage: python generate_identity_image.py <source_image> [--skip-views]")
        print()
        print("This script takes a single user photo and:")
        print("  1. Generates 5 clean headshot views (front, profiles, 3/4 angles)")
        print("  2. Uses those as reference images for character consistency")
        print("  3. Generates the final identity image")
        print()
        print("Options:")
        print("  --skip-views    Skip step 1, reuse existing character views")
        print()
        print("Examples:")
        print("  python generate_identity_image.py server/services/gemini/images/reference/face_only/casey_01.png")
        print("  python generate_identity_image.py server/services/gemini/images/reference/face_only/casey_01.png --skip-views")
        sys.exit(1)
    
    source_image_path = args[0]
    
    if not os.path.exists(source_image_path):
        print(f"ERROR: Source image not found: {source_image_path}")
        sys.exit(1)
    
    source_basename = os.path.splitext(os.path.basename(source_image_path))[0]
    
    # Initialize client
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    print("=" * 60)
    print("IDENTITY IMAGE GENERATION")
    print("=" * 60)
    print(f"Source photo: {source_image_path}")
    print(f"Identity: {IDENTITY_NAME}")
    print()
    
    # Step 1: Generate or reuse character views
    if skip_views:
        # Check for existing character views
        reference_paths = get_existing_character_views(source_basename)
        if not reference_paths:
            print("ERROR: --skip-views specified but no existing character views found")
            print(f"Expected files in: {CHARACTER_VIEWS_DIR}/{source_basename}_*.png")
            sys.exit(1)
        print(f"Skipping character view generation, using {len(reference_paths)} existing views")
        print()
    else:
        # Generate new character views
        reference_paths = generate_character_views(client, source_image_path)
        if not reference_paths:
            print("ERROR: Failed to generate any character views")
            sys.exit(1)
        print()
    
    # Step 2: Generate identity image using the headshots
    output_path = generate_identity_image(client, reference_paths)
    
    # Summary
    print()
    print("=" * 60)
    print("COMPLETE")
    print("=" * 60)
    if not skip_views:
        print(f"Generated {len(reference_paths)} character views in: {CHARACTER_VIEWS_DIR}/")
    else:
        print(f"Reused {len(reference_paths)} existing character views")
    if output_path:
        print(f"Identity image: {output_path}")
    else:
        print("Failed to generate identity image")


if __name__ == "__main__":
    main()
