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

prompt = "We're creating Identity Images for this person. One of thier Identities is Conductor. This Identity is their Doer Of Things Category. It represents the user's role in managing tasks and responsibilities, akin to leading an orchestra. Create a professional, confident, and authoritative image for this Identity. It is important that the user is able to see themselves as a conductor, and that the image is a good representation of their Identity. Keeping thier face in tact is of the utmost importance. If their face isn't exactly right, the effect will be ruined. They must see themselves in the image and if the face is off even a little, it won't work. The image should be an inspiring and motivating picture of them living as this Identity. This image should be an ideal image of them living as this Identity. Nothing negative should be conveyed. Give it a movie poster quality."
aspect_ratio = "16:9"  # "1:1","2:3","3:2","3:4","4:3","4:5","5:4","9:16","16:9","21:9"
resolution = "4K"  # "1K", "2K", "4K"

image = Image.open(
    "/Users/caseyschmid/Programming/Business/Head Shots/casey_shot_01.jpg"
)

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[
        prompt,
        Image.open(
            "/Users/caseyschmid/Programming/Business/Head Shots/casey_shot_01.jpg"
        ),
        Image.open(
            "/Users/caseyschmid/Programming/Business/Head Shots/casey_shot_02.jpg"
        ),
    ],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        image_config=types.ImageConfig(
            aspect_ratio=aspect_ratio,
            image_size=resolution
        ),
    )
)

for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = part.as_image()
        image.save("server/services/gemini/images/conductor_nano_banana_pro_06.png")
