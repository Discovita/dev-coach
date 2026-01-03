#!/usr/bin/env python3

import os
import base64
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
script_path = Path(__file__).resolve()
current = script_path.parent
server_dir = None

while current != current.parent:
    if current.name == "server":
        server_dir = current
        break
    current = current.parent

if server_dir:
    env_path = server_dir / ".env"
    load_dotenv(env_path)
else:
    script_dir = Path(__file__).parent
    server_dir = script_dir.parents[4]
    env_path = server_dir / ".env"
    load_dotenv(env_path)


def main():
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python edit_image.py <input_image_path> <prompt> [output_path]")
        sys.exit(1)
    
    input_image_path = sys.argv[1]
    prompt = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else "server/services/ai/openai_service/scripts/images/edited_image.png"
    
    api_key = os.getenv("NEW_OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    
    # Encode image as base64 for Responses API
    with open(input_image_path, "rb") as f:
        image_bytes = f.read()
        image_base64_encoded = base64.b64encode(image_bytes).decode("utf-8")
        image_url = f"data:image/png;base64,{image_base64_encoded}"
    
    response = client.responses.create(
        model="gpt-5",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": image_url,
                    },
                ],
            }
        ],
        tools=[{"type": "image_generation", "input_fidelity": "high"}],
    )
    
    image_data = [
        output.result
        for output in response.output
        if output.type == "image_generation_call"
    ]
    
    image_base64 = image_data[0]
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "wb") as f:
        f.write(base64.b64decode(image_base64))
    print(f"✅ Image saved to: {output_file.absolute()}")


if __name__ == "__main__":
    main()

# python server/services/ai/openai_service/scripts/edit_image.py '/Users/caseyschmid/Programming/Business/Head Shots/casey_shot_01.jpg' "We're creating Identity Images for this person. One of thier Identities is Conductor. This Identity is their Doer Of Things Category. It represents the user's role in managing tasks and responsibilities, akin to leading an orchestra. Create a professional, confident, and authoritative image for this Identity. It is important that the user is able to see themselves as a conductor, and that the image is a good representation of their Identity. Keeping thier face in tact is of the utmost importance." server/services/ai/openai_service/scripts/images/conductor.png