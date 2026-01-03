#!/usr/bin/env python3

import os
import sys
import base64
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env in server directory
# Navigate up from: server/services/ai/openai_service/scripts/
# To: server/.env
# Find the 'server' directory by walking up the path
script_path = Path(__file__).resolve()
current = script_path.parent
server_dir = None

# Walk up the directory tree to find 'server' directory
while current != current.parent:  # Stop at filesystem root
    if current.name == "server":
        server_dir = current
        break
    current = current.parent

if server_dir:
    env_path = server_dir / ".env"
    load_dotenv(env_path)
else:
    # Fallback: try relative path calculation
    script_dir = Path(__file__).parent
    server_dir = script_dir.parents[4]
    env_path = server_dir / ".env"
    load_dotenv(env_path)


def main():
    api_key = os.getenv("NEW_OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model="gpt-5",
        input="Generate an image of gray tabby cat hugging an otter with an orange scarf",
        tools=[{"type": "image_generation"}],
    )

    # Save the image to a file
    image_data = [
        output.result
        for output in response.output
        if output.type == "image_generation_call"
    ]

    if image_data:
        image_base64 = image_data[0]
        with open("otter.png", "wb") as f:
            f.write(base64.b64decode(image_base64))


if __name__ == "__main__":
    main()
