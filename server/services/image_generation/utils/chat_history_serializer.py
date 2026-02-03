"""
Chat History Serialization Utilities

Functions for serializing and deserializing Gemini chat history
to/from JSON for database storage.
"""

from typing import List

from google.genai.types import Content

from services.logger import configure_logging

log = configure_logging(__name__)


def serialize_chat_history(history: List[Content]) -> List[dict]:
    """
    Serialize Gemini chat history for database storage.

    The Google genai SDK's Content model uses pydantic with:
    - ser_json_bytes='base64': bytes (images, thought signatures) become base64 strings
    - val_json_bytes='base64': base64 strings become bytes on load

    Args:
        history: List of Content objects from chat.get_history()

    Returns:
        List of JSON-serializable dicts
    """
    result = []
    for content in history:
        # Handle both Content objects and dicts (for testing/mocking)
        if isinstance(content, dict):
            result.append(content)
        else:
            result.append(content.to_json_dict())
    return result


def deserialize_chat_history(history_data: List[dict]) -> List[Content]:
    """
    Deserialize stored chat history back to Content objects.

    Args:
        history_data: List of dicts from database JSONField

    Returns:
        List of Content objects for restoring a chat session
    """
    return [Content.model_validate(item) for item in history_data]
