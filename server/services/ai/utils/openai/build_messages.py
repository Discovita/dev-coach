"""
build_messages

Constructs the list of message dicts expected by the OpenAI chat completions
API from a system prompt and optional chat history.

Role mapping:
    'coach'  →  'assistant'   (our DB role → OpenAI API role)
    all other roles are passed through unchanged
"""

from typing import List, Optional

from openai.types.chat import ChatCompletionMessageParam

from apps.chat_messages.models import ChatMessage


def build_messages(
    system_message: Optional[str] = None,
    messages: Optional[List[ChatMessage]] = None,
) -> List[ChatCompletionMessageParam]:
    """
    Build the OpenAI message array from a system prompt and optional chat history.

    Parameters
    ----------
    system_message : str, optional
        Inserted as the first message with role 'system'.
    messages : list of ChatMessage, optional
        Conversation history. The 'coach' role is remapped to 'assistant'.

    Returns
    -------
    List[ChatCompletionMessageParam]
        Ordered message array ready to send to the OpenAI API.
    """
    result: List[ChatCompletionMessageParam] = []

    if system_message:
        result.append({"role": "system", "content": system_message})

    if messages:
        for msg in messages:
            role = "assistant" if msg.role == "coach" else msg.role
            result.append({"role": role, "content": msg.content})

    return result
