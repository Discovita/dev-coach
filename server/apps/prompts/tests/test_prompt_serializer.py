"""
Tests for the PromptSerializer.
"""

from django.test import TestCase

from apps.prompts.models import Prompt
from apps.prompts.serializers import PromptSerializer
from enums.coaching_phase import CoachingPhase
from enums.prompt_type import PromptType


class PromptSerializerTests(TestCase):
    """Tests for PromptSerializer field handling and read-only enforcement."""

    def setUp(self):
        self.prompt = Prompt.objects.create(
            coaching_phase=CoachingPhase.INTRODUCTION,
            prompt_type=PromptType.COACH,
            version=1,
            name="Intro v1",
            description="First intro prompt",
            body="Welcome to coaching.",
        )

    def test_serializes_all_fields(self):
        """All declared fields are present in serialized output."""
        data = PromptSerializer(self.prompt).data

        expected_fields = {
            "id",
            "coaching_phase",
            "version",
            "name",
            "description",
            "body",
            "required_context_keys",
            "allowed_actions",
            "prompt_type",
            "is_active",
            "created_at",
            "updated_at",
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_read_only_fields_not_writable(self):
        """id, created_at, updated_at cannot be set via the serializer."""
        serializer = PromptSerializer(
            data={
                "id": "00000000-0000-0000-0000-000000000001",
                "version": 99,
                "body": "Test body",
                "coaching_phase": CoachingPhase.GET_TO_KNOW_YOU,
                "prompt_type": PromptType.COACH,
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()

        self.assertNotEqual(str(instance.id), "00000000-0000-0000-0000-000000000001")

    def test_body_is_required(self):
        """Serializer rejects data without a body."""
        serializer = PromptSerializer(
            data={"coaching_phase": CoachingPhase.INTRODUCTION}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("body", serializer.errors)

    def test_serializes_existing_instance(self):
        """Round-trip: serialized data matches the model instance."""
        data = PromptSerializer(self.prompt).data

        self.assertEqual(data["coaching_phase"], CoachingPhase.INTRODUCTION)
        self.assertEqual(data["prompt_type"], PromptType.COACH)
        self.assertEqual(data["body"], "Welcome to coaching.")
        self.assertEqual(data["version"], 1)
        self.assertTrue(data["is_active"])
