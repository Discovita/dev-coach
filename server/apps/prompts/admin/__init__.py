"""
Django admin configuration for the prompts app.

Exports:
    PromptAdmin: Admin class for the Prompt model.
"""

from apps.prompts.admin.prompt_admin import PromptAdmin

__all__ = [
    "PromptAdmin",
]
