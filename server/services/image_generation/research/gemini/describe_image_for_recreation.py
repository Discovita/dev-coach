"""
Describe Image for Recreation Script

This script takes an image and generates a detailed text description
that can be used to recreate a similar image with character consistency.

The output is a "recreation prompt" - a detailed description of:
- Scene composition and framing
- Lighting (direction, color, mood)
- Subject pose and body language
- Clothing and styling
- Environment and background
- Camera angle and perspective
- Color grading and atmosphere
- Artistic style and quality

This description can then be used with character view images to generate
a new image with the same scene but a different (specific) person.

Usage:
    python describe_image_for_recreation.py

Output:
    Prints the recreation prompt to console and saves to a text file.
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
# CONFIGURATION - HARDCODED INPUT
# Change this to the image you want to describe
# ============================================================================

IMAGE_TO_DESCRIBE = "server/services/gemini/images/generic_identity/conductor_01.png"

# Output file for the description
OUTPUT_FILE = "server/services/gemini/images/generic_identity/conductor_01_description.txt"

# ============================================================================
# RETRY CONFIGURATION
# ============================================================================

MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 5
RETRY_BACKOFF_MULTIPLIER = 2


# ============================================================================
# PROMPT
# ============================================================================

def build_prompt() -> str:
    """
    Build the prompt for describing the image.
    
    We want a description that:
    1. Is detailed enough to recreate the image
    2. Focuses on everything EXCEPT the specific person's face
    3. Is formatted as a prompt that could generate a similar image
    """
    return """Analyze this image and create a detailed description that could be used to recreate it with a different person.

Focus on describing:

1. SCENE & COMPOSITION
   - What is the setting/environment?
   - How is the frame composed? (wide shot, medium shot, close-up, etc.)
   - Where is the subject positioned in the frame?

2. LIGHTING
   - Where is the light coming from? (direction, angle)
   - What type of lighting? (natural, studio, dramatic, soft, hard)
   - What color temperature? (warm golden, cool blue, neutral)
   - Where are the shadows falling?
   - Any special lighting effects? (rim light, backlight, etc.)

3. SUBJECT POSE & BODY LANGUAGE
   - What is the body position and pose?
   - What direction is the person facing?
   - What is the head angle and tilt?
   - What expression/mood is being conveyed?
   - What are the arms/hands doing?

4. CLOTHING & STYLING
   - What is the person wearing? (be specific about style, color, details)
   - Any accessories?

5. BACKGROUND & ENVIRONMENT
   - What's in the background?
   - How blurred/sharp is the background?
   - Any notable environmental elements?

6. CAMERA & TECHNICAL
   - What appears to be the camera angle? (eye level, low angle, high angle)
   - What's the approximate focal length feel? (wide, normal, telephoto)
   - Depth of field? (shallow with bokeh, deep and sharp)

7. COLOR GRADING & ATMOSPHERE
   - Overall color palette
   - Any color grading or toning? (cinematic, warm, cool, desaturated)
   - The mood and atmosphere

8. ARTISTIC STYLE
   - Is this photorealistic, stylized, cinematic?
   - What's the overall quality level? (professional, movie poster, editorial)
   - Any specific artistic references?

DO NOT describe the person's specific facial features (eyes, nose, mouth shape, etc.) - we want to replace them with a different person.

Format your response as a single, flowing prompt that could be used to generate a similar image. Start with the most important elements and flow naturally. Make it detailed but not overly verbose.

Begin the prompt with: "A cinematic, movie-poster quality image of a person..."
"""


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def describe_image(client: genai.Client) -> str | None:
    """
    Generate a detailed description of the image for recreation.
    
    Args:
        client: Gemini API client
    
    Returns:
        The description text, or None if failed
    """
    print("=" * 60)
    print("DESCRIBING IMAGE FOR RECREATION")
    print("=" * 60)
    print(f"Image: {IMAGE_TO_DESCRIBE}")
    print(f"Output: {OUTPUT_FILE}")
    print()
    
    # Load the image
    if not os.path.exists(IMAGE_TO_DESCRIBE):
        print(f"ERROR: Image not found: {IMAGE_TO_DESCRIBE}")
        return None
    
    image = Image.open(IMAGE_TO_DESCRIBE)
    print(f"✓ Loaded image: {IMAGE_TO_DESCRIBE}")
    print()
    
    # Build prompt
    prompt = build_prompt()
    
    # Build contents: image first, then prompt
    contents = [image, prompt]
    
    # Retry loop
    retry_delay = INITIAL_RETRY_DELAY
    
    for attempt in range(MAX_RETRIES):
        try:
            print("Generating description...")
            
            response = client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT"],  # Text only for this step
                ),
            )
            
            # Extract text from response
            description = None
            for part in response.parts:
                if part.text:
                    description = part.text
                    break
            
            if description:
                print()
                print("=" * 60)
                print("DESCRIPTION")
                print("=" * 60)
                print(description)
                print()
                
                # Save to file
                os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
                with open(OUTPUT_FILE, "w") as f:
                    f.write(description)
                print(f"✓ Saved to: {OUTPUT_FILE}")
                
                return description
            else:
                print("WARNING: No text in response, retrying...")
            
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
                return None
    
    return None


# ============================================================================
# MAIN
# ============================================================================

def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python describe_image_for_recreation.py")
        print()
        print("Generates a detailed description of an image that can be used")
        print("to recreate it with character consistency.")
        print()
        print("Configure by editing the constants at the top of the script:")
        print("  - IMAGE_TO_DESCRIBE: Path to the image to analyze")
        print("  - OUTPUT_FILE: Path to save the description")
        sys.exit(0)
    
    # Initialize client
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Generate description
    description = describe_image(client)
    
    # Summary
    print()
    print("=" * 60)
    print("COMPLETE")
    print("=" * 60)
    if description:
        print(f"Description saved to: {OUTPUT_FILE}")
        print()
        print("Next step: Use this description with character views to generate")
        print("a new image with the same scene but your specific person.")
    else:
        print("Failed to generate description")


if __name__ == "__main__":
    main()
