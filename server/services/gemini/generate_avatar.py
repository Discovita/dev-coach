"""
Avatar Generation Script

Usage:
  python generate_avatar.py                       # Generate 1 headshot at 4K
  python generate_avatar.py --multi               # Generate 3 headshot candidates at 1K  
  python generate_avatar.py path/to/headshot.png  # Skip headshot, generate full body only
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
OUTPUT_DIR = "server/services/gemini/images"

# Whether to show thinking process
SHOW_THINKING = True

# ============================================================================
# PROMPTS
# ============================================================================

HEADSHOT_PROMPT = """Look at the reference photos provided. Study this person's face carefully - their face shape, eyes, nose, mouth, jawline, hairline, and all distinctive features.

Now create a professional headshot of THIS EXACT PERSON.

Shoulders up, facing camera, neutral gray background.
Warm confident smile, bright eyes.
Clean studio lighting with soft edge lighting for depth.

CRITICAL: The output must be recognizably THE SAME PERSON from the reference photos. Do not generate a generic face. Use the reference photos as your guide for every facial feature.

Style: Glamour photography with tasteful retouching.
- Smooth, flawless skin - no visible pores, wrinkles, or blemishes
- Even hair color - no gray or salt-and-pepper, natural consistent tone
- Bright, youthful eyes
- Polished and aspirational - the best version of this specific person
- They should look 5-10 years younger and refreshed

This person should look at the result and immediately recognize themselves.
"""

FULLBODY_PROMPT = """Look at this headshot. This is the person's face - study it carefully.

Now create a full body shot of THIS EXACT PERSON.

Standing straight, facing camera, relaxed confident posture.
Wearing a fitted black t-shirt and dark jeans.
Hands relaxed at sides.
Full frame from head to feet with some padding around edges.
Neutral gray background.

CRITICAL: The face must be IDENTICAL to the headshot provided. Same person, same features, same smile. The body should have average, healthy proportions that match the face.

Style: Professional photography, clean studio lighting.
Polished and aspirational - the best version of this person.
"""

# ============================================================================
# UTILITIES
# ============================================================================

def get_next_avatar_number() -> int:
    """Find the next available number for avatar pairs (headshot + fullbody)."""
    # Look for existing headshot files to determine next number
    pattern = f"{OUTPUT_DIR}/casey_avatar_headshot_nb_*.png"
    existing_files = glob.glob(pattern)
    
    if not existing_files:
        return 1
    
    # Extract numbers from filenames
    numbers = []
    for f in existing_files:
        match = re.search(r'casey_avatar_headshot_nb_(\d+)\.png', f)
        if match:
            numbers.append(int(match.group(1)))
    
    if not numbers:
        return 1
    
    return max(numbers) + 1


# ============================================================================
# STEP 1: Generate headshot from reference photos
# ============================================================================

def generate_headshot(avatar_num: int, multi_mode: bool = False) -> tuple[Image.Image, str]:
    """
    Generate headshot from reference photos.
    
    Args:
        avatar_num: Number for filename
        multi_mode: If True, generates 3 candidates at 1K quality
        
    Returns: (PIL Image, path) of the final/best headshot
    """
    if multi_mode:
        print("Generating 3 headshot candidates at 1K quality...")
        prompt = f"Generate 3 different headshot variations of this person, each with slightly different expressions or angles.\n\n{HEADSHOT_PROMPT}"
        image_size = "1K"
    else:
        print("Generating headshot from reference photos...")
        prompt = HEADSHOT_PROMPT
        image_size = "4K"

    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=[
            Image.open("server/services/gemini/images/reference/casey_regular_shot_01.png"),
            Image.open("server/services/geminiImage /images/reference/casey_regular_shot_02.png"),
            Image.open("server/services/gemini/images/reference/casey_regular_shot_03.png"),
            Image.open("server/services/gemini/images/reference/casey_regular_shot_04.png"),
            Image.open("server/services/gemini/images/reference/casey_shot_05.jpeg"),
            prompt,
        ],
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="3:4", image_size=image_size),
        ),
    )

    # Process response, separating thinking from final output
    thinking_count = 0
    final_count = 0
    final_image = None
    final_path = None
    
    for part in response.parts:
        # Check if this is a thinking part
        is_thinking = getattr(part, 'thought', False)
        
        if is_thinking:
            if SHOW_THINKING:
                if part.text is not None:
                    print(f"  [THINKING] {part.text}")
                elif part.inline_data is not None:
                    thinking_count += 1
                    thinking_path = f"{OUTPUT_DIR}/thinking_{avatar_num:02d}_{thinking_count}.png"
                    thinking_image = part.as_image()
                    thinking_image.save(thinking_path)
                    print(f"  [THINKING IMAGE] Saved: {thinking_path}")
        else:
            # Final output
            if part.text is not None:
                print(f"Response: {part.text}")
            elif part.inline_data is not None:
                final_count += 1
                if multi_mode:
                    headshot_path = f"{OUTPUT_DIR}/casey_avatar_headshot_nb_{avatar_num:02d}_{final_count}.png"
                else:
                    headshot_path = f"{OUTPUT_DIR}/casey_avatar_headshot_nb_{avatar_num:02d}.png"
                
                headshot_image = part.as_image()
                headshot_image.save(headshot_path)
                print(f"Saved headshot: {headshot_path}")
                
                # Keep track of the last one as the "final" image
                final_image = headshot_image
                final_path = headshot_path
    
    if final_image is None:
        print("ERROR: Failed to generate headshot")
        exit(1)
    
    print(f"\nGenerated {final_count} headshot(s), {thinking_count} thinking image(s)")
    
    # Reload from disk to ensure proper format for next API call
    return Image.open(final_path), final_path


# ============================================================================
# STEP 2: Generate full body from headshot
# ============================================================================

def generate_fullbody(headshot_image: Image.Image, avatar_num: int, multi_mode: bool = False) -> Image.Image:
    """Generate full body from headshot. Returns PIL Image."""
    if multi_mode:
        print("Generating full body at 1K quality...")
        image_size = "1K"
    else:
        print("Generating full body from headshot...")
        image_size = "4K"

    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=[
            headshot_image,
            FULLBODY_PROMPT,
        ],
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="2:3", image_size=image_size),
        ),
    )

    fullbody_path = f"{OUTPUT_DIR}/casey_avatar_fullbody_nb_{avatar_num:02d}.png"
    
    # Process response, separating thinking from final output
    thinking_count = 0
    final_image = None

    for part in response.parts:
        is_thinking = getattr(part, 'thought', False)
        
        if is_thinking:
            if SHOW_THINKING:
                if part.text is not None:
                    print(f"  [THINKING] {part.text}")
                elif part.inline_data is not None:
                    thinking_count += 1
                    thinking_path = f"{OUTPUT_DIR}/thinking_fullbody_{avatar_num:02d}_{thinking_count}.png"
                    thinking_image = part.as_image()
                    thinking_image.save(thinking_path)
                    print(f"  [THINKING IMAGE] Saved: {thinking_path}")
        else:
            if part.text is not None:
                print(f"Response: {part.text}")
            elif part.inline_data is not None:
                fullbody_image = part.as_image()
                fullbody_image.save(fullbody_path)
                print(f"Saved full body: {fullbody_path}")
                final_image = fullbody_image

    if final_image is None:
        print("ERROR: Failed to generate full body")
        exit(1)
    
    if thinking_count > 0:
        print(f"  ({thinking_count} thinking images generated)")
    
    return final_image


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Parse arguments
    multi_mode = "--multi" in sys.argv
    headshot_path_arg = None
    
    for arg in sys.argv[1:]:
        if arg != "--multi" and not arg.startswith("--"):
            headshot_path_arg = arg
            break
    
    # Get next available avatar number for paired naming
    avatar_num = get_next_avatar_number()
    print(f"Using avatar number: {avatar_num:02d}")
    
    if multi_mode:
        print("MULTI MODE: Generating 3 candidates at 1K quality")
    
    # Check if headshot path provided as argument
    if headshot_path_arg:
        print(f"Using existing headshot: {headshot_path_arg}")
        headshot_image = Image.open(headshot_path_arg)
        # Generate full body from provided headshot
        generate_fullbody(headshot_image, avatar_num, multi_mode)
    else:
        # Generate headshot from reference photos
        headshot_image, _ = generate_headshot(avatar_num, multi_mode)
        
        # Only generate full body if not in multi mode (pick best headshot first)
        if not multi_mode:
            generate_fullbody(headshot_image, avatar_num, multi_mode)
        else:
            print("\nMulti mode: Review headshots and re-run with chosen one:")
            print(f"  python generate_avatar.py {OUTPUT_DIR}/casey_avatar_headshot_nb_{avatar_num:02d}_X.png")

    print("Done!")
