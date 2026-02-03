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

prompt = """Prompt Goes Here"""

aspect_ratio = "3:4"  # "1:1","2:3","3:2","3:4","4:3","4:5","5:4","9:16","16:9","21:9"
resolution = "4K"  # "1K", "2K", "4K"


response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[
        Image.open(
            "server/services/image_generation/research/gemini/images/game_flashcards_03.png"
        ),
        # Image.open("/Users/caseyschmid/Desktop/Screenshot 2026-01-25 at 11.26.18.png"),
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
        image.save(
            "server/services/image_generation/research/gemini/images/game_flashcards_04.png"
        )
