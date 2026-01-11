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

prompt = """Look at the reference photos provided. Study this person's face carefully - their face shape, eyes, nose, mouth, jawline, hairline, and all distinctive features.

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

aspect_ratio = "3:4"  # "1:1","2:3","3:2","3:4","4:3","4:5","5:4","9:16","16:9","21:9"
resolution = "4K"  # "1K", "2K", "4K"


response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[
        Image.open("server/services/gemini/images/reference/casey_regular_shot_01.png"),
        Image.open("server/services/gemini/images/reference/casey_regular_shot_02.png"),
        Image.open("server/services/gemini/images/reference/casey_regular_shot_03.png"),
        Image.open("server/services/gemini/images/reference/casey_regular_shot_04.png"),
        Image.open("server/services/gemini/images/reference/casey_shot_05.jpeg"),
        prompt,
    ],
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(
            aspect_ratio=aspect_ratio, image_size=resolution
        ),
    ),
)

for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = part.as_image()
        image.save("server/services/gemini/images/casey_avatar.png")
