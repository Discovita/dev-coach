"""
Prompt viewsets.

Exports:
    PromptViewSet: Admin-only CRUD and utility endpoints for prompts.
"""

from apps.prompts.views.prompt_view_set import PromptViewSet

__all__ = [
    "PromptViewSet",
]
