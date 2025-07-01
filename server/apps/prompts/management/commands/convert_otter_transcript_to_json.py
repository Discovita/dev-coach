import os
import re
import json

from bs4 import BeautifulSoup, Comment
from django.core.management.base import BaseCommand

# ------ CONFIGURE LOGGING ------
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")

base_dir_path = "services/prompt_manager/prompts/examples/"
raw_dir_path = os.path.join(base_dir_path, "raw_otter_transcripts/")
processed_dir_path = os.path.join(base_dir_path, "processed_otter_transcripts/")
json_dir_path = os.path.join(base_dir_path, "json/")


def remove_empty_tags(soup):
    removed = True
    while removed:
        removed = False
        for tag in soup.find_all():
            if not tag.contents or all(
                (isinstance(child, str) and not child.strip()) for child in tag.contents
            ):
                tag.decompose()
                removed = True


def pre_process_html(file_name):
    file_path = os.path.join(raw_dir_path, file_name)
    pre_processed_file_path = os.path.join(processed_dir_path, file_name)
    os.makedirs(os.path.dirname(pre_processed_file_path), exist_ok=True)
    with open(file_path, "r") as file:
        soup = BeautifulSoup(file.read(), "html.parser")
    # Remove all HTML comments (including <!---->)
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # remove all tag attributes
    for tag in soup.find_all(True):
        tag.attrs = {}

    # Remove all <app-reangular-avatar> tags and their contents
    for avatar_tag in soup.find_all("app-reangular-avatar"):
        avatar_tag.decompose()

    # Unwrap all <span> tags (remove the tag but keep its contents)
    for span_tag in soup.find_all("span"):
        span_tag.unwrap()

    # Recursively remove only truly empty tags (tags with no content and no children)

    # remove_empty_tags(soup)

    # Rename the root <div> to <section> before processing the divs
    all_divs = soup.find_all("div")
    if all_divs:
        all_divs[0].name = "section"

    # Process all <div> tags except the root (now <section>)
    divs = soup.find_all("div")
    for div in divs:
        direct_texts = [
            t for t in div.find_all(text=True, recursive=False) if t.strip()
        ]
        if direct_texts:
            continue  # keep <div> with direct text
        elif div.contents:
            div.unwrap()  # unwrap <div> with children but no direct text
        else:
            div.decompose()  # remove truly empty <div>

    with open(pre_processed_file_path, "w") as file:
        file.write(str(soup))
    return pre_processed_file_path


def convert_html_to_json(pre_processed_file_path, json_file_path):
    with open(pre_processed_file_path, "r") as file:
        soup = BeautifulSoup(file.read(), "html.parser")
    data = []
    for snippet in soup.find_all("app-conversation-transcript-snippet"):
        divs = snippet.find_all("div", recursive=False)
        if len(divs) >= 3:
            speaker = divs[0].get_text(strip=True)
            timestamp = divs[1].get_text(strip=True)
            content = divs[2].get_text(" ", strip=True)
            data.append(
                {
                    "speaker": speaker,
                    "timestamp": timestamp,
                    "content": content,
                    "coach_phase": "",
                }
            )
    with open(json_file_path, "w") as f:
        json.dump(data, f, indent=2)


class Command(BaseCommand):
    help = "Convert Otter transcripts to JSON"

    def handle(self, *args, **options):
        os.makedirs(json_dir_path, exist_ok=True)
        for i, file_name in enumerate(os.listdir(raw_dir_path)):
            log.step(f"Processing file {i+1}: {file_name}")
            json_file_name = os.path.splitext(file_name)[0] + ".json"
            json_file_path = os.path.join(json_dir_path, json_file_name)
            if os.path.exists(json_file_path):
                log.warning(f"JSON file already exists for {file_name}. Skipping...")
                continue
            pre_processed_file_path = pre_process_html(file_name)
            self.stdout.write(self.style.NOTICE("PreProcessed HTML"))
            convert_html_to_json(pre_processed_file_path, json_file_path)
        self.stdout.write(self.style.SUCCESS("Done!"))
