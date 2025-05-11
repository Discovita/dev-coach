"""
Utility for prepending system context to system messages for prompt generation.
Used by prompt_manager.manager and other prompt modules to add system context from prompts/system_context.md.
"""

import os


def prepend_system_context(
    system_message: str,
) -> str:
    """
    Prepend the system context from prompts/system_context.md to the given system message.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    system_context_path = os.path.join(
        current_dir, "..", "prompts", "system_context.md"
    )
    try:
        with open(system_context_path, "r", encoding="utf-8") as f:
            system_context = f.read().strip()
    except Exception as e:
        system_context = ""
    if system_context:
        return f"{system_context}\n\n{system_message}"
    else:
        return system_message
