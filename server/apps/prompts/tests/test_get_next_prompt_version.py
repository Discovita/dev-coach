"""
Tests for the get_next_prompt_version utility.
"""

from django.test import TestCase

from apps.prompts.models import Prompt
from apps.prompts.utils import get_next_prompt_version
from enums.coaching_phase import CoachingPhase
from enums.prompt_type import PromptType


class GetNextPromptVersionTests(TestCase):
    """Tests for version auto-assignment logic."""

    def test_first_version_for_new_phase(self):
        """Returns 1 when no prompts exist for the given scope."""
        version = get_next_prompt_version(PromptType.COACH, CoachingPhase.INTRODUCTION)
        self.assertEqual(version, 1)

    def test_increments_existing_version(self):
        """Returns latest + 1 when prompts already exist."""
        Prompt.objects.create(
            coaching_phase=CoachingPhase.INTRODUCTION,
            prompt_type=PromptType.COACH,
            version=1,
            body="v1",
        )
        Prompt.objects.create(
            coaching_phase=CoachingPhase.INTRODUCTION,
            prompt_type=PromptType.COACH,
            version=3,
            body="v3",
        )

        version = get_next_prompt_version(PromptType.COACH, CoachingPhase.INTRODUCTION)
        self.assertEqual(version, 4)

    def test_scoped_to_prompt_type(self):
        """Different prompt_types have independent version sequences."""
        Prompt.objects.create(
            coaching_phase=CoachingPhase.INTRODUCTION,
            prompt_type=PromptType.COACH,
            version=5,
            body="coach v5",
        )

        version = get_next_prompt_version(PromptType.SYSTEM, CoachingPhase.INTRODUCTION)
        self.assertEqual(version, 1)

    def test_scoped_to_coaching_phase(self):
        """Different coaching_phases have independent version sequences."""
        Prompt.objects.create(
            coaching_phase=CoachingPhase.INTRODUCTION,
            prompt_type=PromptType.COACH,
            version=5,
            body="intro v5",
        )

        version = get_next_prompt_version(
            PromptType.COACH, CoachingPhase.GET_TO_KNOW_YOU
        )
        self.assertEqual(version, 1)

    def test_null_coaching_phase(self):
        """Prompts without coaching_phase are versioned independently."""
        Prompt.objects.create(
            coaching_phase=None,
            prompt_type=PromptType.SENTINEL,
            version=2,
            body="sentinel v2",
        )

        version = get_next_prompt_version(PromptType.SENTINEL, None)
        self.assertEqual(version, 3)

    def test_null_coaching_phase_does_not_mix_with_non_null(self):
        """coaching_phase=None scope is separate from any named phase."""
        Prompt.objects.create(
            coaching_phase=CoachingPhase.INTRODUCTION,
            prompt_type=PromptType.COACH,
            version=10,
            body="intro v10",
        )

        version = get_next_prompt_version(PromptType.COACH, None)
        self.assertEqual(version, 1)
