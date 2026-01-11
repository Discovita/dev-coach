"""
Face Swap Avatar Generation Script (Method 3)

This script implements the two-step approach:
1. Generate a generic identity image based on body description constants
2. Face swap the user's face onto that generated image

Usage:
  python face_swap.py                         # Generate new intermediate + face swap
  python face_swap.py path/to/image.png       # Use provided image as intermediate + face swap
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

# Output directory
OUTPUT_DIR = "server/services/gemini/images/face_swap"

# Whether to show thinking process
SHOW_THINKING = True

# ============================================================================
# IMAGE CONFIG CONSTANTS
# Toggle these to change output image settings
# ============================================================================

# Aspect ratio options: "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"
ASPECT_RATIO = "16:9"

# Resolution options: "1K", "2K", "4K"
RESOLUTION = "4K"

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
# IDENTITY CONSTANTS
# Toggle these to test different identities
# ============================================================================

# Identity Name: The name of the identity being visualized
IDENTITY_NAME = "Conductor"

# Category: The identity category (e.g., "Passions & Talents", "Career & Purpose", etc.)
IDENTITY_CATEGORY = "Passions & Talents"

# I Am Statement: Optional - the "I Am" statement for this identity
IDENTITY_I_AM_STATEMENT = None  # e.g., "I am someone who brings harmony and direction to creative endeavors"

# Visualization: Optional - the visualization text for this identity
IDENTITY_VISUALIZATION = None  # e.g., "I see myself standing confidently in a modern office..."

# Notes: Optional - list of notes about this identity
IDENTITY_NOTES = None  # e.g., ["Focus on leadership", "Emphasize creativity"]

# ============================================================================
# REFERENCE IMAGES
# These are the face reference images for the face swap step
# ============================================================================
REFERENCE_IMAGES = [
    "server/services/gemini/images/reference/face_only/casey_01.png",
    "server/services/gemini/images/reference/face_only/casey_02.png",
    "server/services/gemini/images/reference/face_only/casey_03.png",
    "server/services/gemini/images/reference/face_only/casey_04.png",
    "server/services/gemini/images/reference/face_only/casey_05.png",
]

# ============================================================================
# PROMPTS
# Based on the current image generation prompt from seed_image_generation_prompt.py
# ============================================================================

def get_identity_context() -> str:
    """
    Format identity context for the prompt.
    Matches the format used by get_identity_context_for_image() in the codebase.
    
    Returns:
        Formatted string with identity details
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


def get_generic_identity_prompt() -> str:
    """
    Build the prompt for generating a generic identity image.
    Based on the current image generation prompt, but adapted for Method 3:
    - Uses body description constants and identity context
    - Removes face preservation requirement (we'll swap it in step 2)
    - Focuses on body type, pose, scene, and aesthetic
    
    The face doesn't matter - we just need the body type, pose, and scene right.
    """
    body_description = f"a {HEIGHT} {BUILD} {ETHNICITY} {GENDER} {AGE} with {HAIR}"
    identity_context = get_identity_context()
    
    # Based on the current image generation prompt structure:
    # "We're creating an Identity Image for this person."
    # "{identity_context}"
    # "Create a professional, confident, and inspiring image for this Identity."
    # "It is critical that the person's face remains intact and recognizable."
    # "The image should be an ideal visualization of them living as this Identity."
    # "Give it a movie poster quality aesthetic."
    # "Nothing negative should be conveyed - this is an aspirational image."
    
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

def get_next_face_swap_number() -> int:
    """Find the next available number for face swap outputs."""
    pattern = f"{OUTPUT_DIR}/face_swap_final_*.png"
    existing_files = glob.glob(pattern)
    
    if not existing_files:
        return 1
    
    numbers = []
    for f in existing_files:
        match = re.search(r'face_swap_final_(\d+)\.png', f)
        if match:
            numbers.append(int(match.group(1)))
    
    if not numbers:
        return 1
    
    return max(numbers) + 1


# ============================================================================
# STEP 1: Generate Generic Identity Image
# ============================================================================

def generate_generic_identity(run_num: int) -> tuple[Image.Image, str]:
    """
    Generate a generic identity image based on body description constants.
    The face doesn't matter - we're going to swap it out in step 2.
    
    Args:
        run_num: Number for filename
        
    Returns: (PIL Image, path) of the generated image
    """
    print("=" * 60)
    print("STEP 1: Generating Generic Identity Image")
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
    intermediate_path = f"{OUTPUT_DIR}/face_swap_intermediate_{run_num:02d}.png"
    
    for part in response.parts:
        is_thinking = getattr(part, 'thought', False)
        
        if is_thinking:
            if SHOW_THINKING:
                if part.text is not None:
                    print(f"  [THINKING] {part.text}")
                elif part.inline_data is not None:
                    thinking_count += 1
                    thinking_path = f"{OUTPUT_DIR}/face_swap_thinking_{run_num:02d}_{thinking_count}.png"
                    thinking_image = part.as_image()
                    thinking_image.save(thinking_path)
                    print(f"  [THINKING IMAGE] Saved: {thinking_path}")
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
    
    if thinking_count > 0:
        print(f"  ({thinking_count} thinking images generated)")
    
    # Reload from disk to ensure proper format for next API call
    return Image.open(intermediate_path), intermediate_path


# ============================================================================
# STEP 2: Face Swap
# ============================================================================

def face_swap(intermediate_image: Image.Image, run_num: int) -> Image.Image:
    """
    Swap the face in the intermediate image with the user's face from reference images.
    
    Args:
        intermediate_image: The generic identity image to modify
        run_num: Number for filename
        
    Returns: PIL Image with face swapped
    """
    print()
    print("=" * 60)
    print("STEP 2: Face Swap")
    print("=" * 60)
    print(f"Using {len(REFERENCE_IMAGES)} reference images for face swap")
    print()
    
    # Load reference images
    reference_images = []
    for ref_path in REFERENCE_IMAGES:
        if os.path.exists(ref_path):
            reference_images.append(Image.open(ref_path))
            print(f"  Loaded: {ref_path}")
        else:
            print(f"  WARNING: Reference image not found: {ref_path}")
    
    if not reference_images:
        print("ERROR: No reference images found!")
        sys.exit(1)
    
    print()
    
    # Build content list: reference faces first to establish the person,
    # then the scene image, then the instruction
    # This tells the model "here's the person" -> "here's the scene" -> "put this person in this scene"
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
    thinking_count = 0
    final_image = None
    final_path = f"{OUTPUT_DIR}/face_swap_final_{run_num:02d}.png"
    
    for part in response.parts:
        is_thinking = getattr(part, 'thought', False)
        
        if is_thinking:
            if SHOW_THINKING:
                if part.text is not None:
                    print(f"  [THINKING] {part.text}")
                elif part.inline_data is not None:
                    thinking_count += 1
                    thinking_path = f"{OUTPUT_DIR}/face_swap_thinking_swap_{run_num:02d}_{thinking_count}.png"
                    thinking_image = part.as_image()
                    thinking_image.save(thinking_path)
                    print(f"  [THINKING IMAGE] Saved: {thinking_path}")
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
    
    if thinking_count > 0:
        print(f"  ({thinking_count} thinking images generated)")
    
    return final_image


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Parse arguments
    # Usage:
    #   python face_swap.py                              # Generate new intermediate + face swap
    #   python face_swap.py path/to/image.png            # Use provided image as intermediate + face swap
    
    provided_intermediate_path = None
    for arg in sys.argv[1:]:
        if not arg.startswith("--") and os.path.exists(arg):
            provided_intermediate_path = arg
            break
    
    # Get next available run number
    run_num = get_next_face_swap_number()
    print(f"Run number: {run_num:02d}")
    print()
    
    if provided_intermediate_path:
        # Use provided intermediate image
        print(f"Using provided intermediate image: {provided_intermediate_path}")
        intermediate_image = Image.open(provided_intermediate_path)
        
        # Save a copy as the intermediate for this run
        intermediate_save_path = f"{OUTPUT_DIR}/face_swap_intermediate_{run_num:02d}.png"
        intermediate_image.save(intermediate_save_path)
        print(f"Saved copy as: {intermediate_save_path}")
    else:
        # Step 1: Generate generic identity image
        intermediate_image, _ = generate_generic_identity(run_num)
    
    # Step 2: Face swap
    final_image = face_swap(intermediate_image, run_num)
    
    print()
    print("=" * 60)
    print("DONE!")
    print("=" * 60)
    print(f"Intermediate image: {OUTPUT_DIR}/face_swap_intermediate_{run_num:02d}.png")
    print(f"Final image: {OUTPUT_DIR}/face_swap_final_{run_num:02d}.png")
