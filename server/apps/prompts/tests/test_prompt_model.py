"""
Tests for the Prompt model.
"""

import uuid

from django.db import IntegrityError
from django.test import TestCase

from apps.prompts.models import Prompt
from enums.coaching_phase import CoachingPhase
from enums.prompt_type import PromptType


class PromptModelTests(TestCase):
    """Tests for Prompt model fields, defaults, and constraints."""

    def test_create_prompt_with_defaults(self):
        """Verify a prompt is created with correct default values."""
        prompt = Prompt.objects.create(
            coaching_phase=CoachingPhase.INTRODUCTION,
            body="Hello, I am your coach.",
        )

        self.assertIsInstance(prompt.id, uuid.UUID)
        self.assertEqual(prompt.coaching_phase, CoachingPhase.INTRODUCTION)
        self.assertEqual(prompt.version, 1)
        self.assertEqual(prompt.prompt_type, PromptType.COACH)
        self.assertTrue(prompt.is_active)
        self.assertIsNone(prompt.name)
        self.assertIsNone(prompt.description)
        self.assertEqual(prompt.required_context_keys, [])
        self.assertEqual(prompt.allowed_actions, [])
        self.assertIsNotNone(prompt.created_at)
        self.assertIsNotNone(prompt.updated_at)

    def test_create_prompt_without_coaching_phase(self):
        """Prompts like sentinel/image_generation may omit coaching_phase."""
        prompt = Prompt.objects.create(
            prompt_type=PromptType.SENTINEL,
            body="Sentinel prompt body",
        )

        self.assertIsNone(prompt.coaching_phase)
        self.assertEqual(prompt.prompt_type, PromptType.SENTINEL)

    def test_create_prompt_with_all_fields(self):
        """Verify all optional fields can be populated."""
        prompt = Prompt.objects.create(
            coaching_phase=CoachingPhase.GET_TO_KNOW_YOU,
            version=3,
            name="GTKY v3",
            description="Third version of the get-to-know-you prompt",
            body="Tell me about yourself.",
            prompt_type=PromptType.COACH,
            is_active=False,
        )

        self.assertEqual(prompt.name, "GTKY v3")
        self.assertEqual(prompt.version, 3)
        self.assertFalse(prompt.is_active)

    def test_unique_together_constraint(self):
        """The (prompt_type, coaching_phase, version) triple must be unique."""
        Prompt.objects.create(
            coaching_phase=CoachingPhase.INTRODUCTION,
            prompt_type=PromptType.COACH,
            version=1,
            body="Version 1",
        )

        with self.assertRaises(IntegrityError):
            Prompt.objects.create(
                coaching_phase=CoachingPhase.INTRODUCTION,
                prompt_type=PromptType.COACH,
                version=1,
                body="Duplicate version 1",
            )

    def test_unique_together_allows_different_phases(self):
        """Same version is allowed for different coaching phases."""
        Prompt.objects.create(
            coaching_phase=CoachingPhase.INTRODUCTION,
            prompt_type=PromptType.COACH,
            version=1,
            body="Intro v1",
        )
        prompt2 = Prompt.objects.create(
            coaching_phase=CoachingPhase.GET_TO_KNOW_YOU,
            prompt_type=PromptType.COACH,
            version=1,
            body="GTKY v1",
        )

        self.assertEqual(prompt2.version, 1)

    def test_unique_together_allows_different_prompt_types(self):
        """Same version + phase is allowed for different prompt types."""
        Prompt.objects.create(
            coaching_phase=CoachingPhase.INTRODUCTION,
            prompt_type=PromptType.COACH,
            version=1,
            body="Coach v1",
        )
        prompt2 = Prompt.objects.create(
            coaching_phase=CoachingPhase.INTRODUCTION,
            prompt_type=PromptType.SYSTEM,
            version=1,
            body="System v1",
        )

        self.assertEqual(prompt2.prompt_type, PromptType.SYSTEM)

    def test_uuid_primary_key_is_unique(self):
        """Each prompt gets a distinct UUID."""
        p1 = Prompt.objects.create(body="One", version=1)
        p2 = Prompt.objects.create(body="Two", version=2)

        self.assertNotEqual(p1.id, p2.id)
