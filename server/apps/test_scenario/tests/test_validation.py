"""
Tests for the validate_scenario_template utility.

Covers valid templates, missing required fields, extra/invalid fields,
type mismatches, and edge cases (empty sections, nulls).
"""

from django.test import TestCase

from apps.test_scenario.utils import validate_scenario_template

VALID_TEMPLATE = {
    "user": {
        "email": "test@example.com",
        "password": "Coach123!",
        "first_name": "Test",
        "last_name": "User",
    },
    "coach_state": {
        "current_phase": "IDENTITY_BRAINSTORMING",
        "identity_focus": "PASSIONS",
        "who_you_are": ["Curious Explorer"],
        "who_you_want_to_be": ["Visionary Leader"],
    },
    "identities": [
        {"name": "Curious Explorer", "category": "PASSIONS", "state": "ACCEPTED"}
    ],
    "chat_messages": [
        {"role": "USER", "content": "I'm ready to brainstorm new identities."}
    ],
    "user_notes": [{"note": "User is highly motivated at this stage."}],
}

MINIMAL_VALID_TEMPLATE = {
    "user": {
        "email": "test@example.com",
        "password": "Coach123!",
        "first_name": "Test",
        "last_name": "User",
    }
}


class TestValidateScenarioTemplate(TestCase):
    """Tests for validate_scenario_template()."""

    def test_valid_template_passes(self):
        errors = validate_scenario_template(VALID_TEMPLATE)
        self.assertEqual(errors, [])

    def test_all_optional_fields_present(self):
        template = {
            "user": {
                "email": "test2@example.com",
                "password": "Coach123!",
                "first_name": "Optional",
                "last_name": "Fields",
                "is_active": True,
                "is_superuser": False,
                "is_staff": False,
                "verification_token": "abc123",
                "email_verification_sent_at": "2024-01-01T00:00:00Z",
            },
            "coach_state": {
                "current_phase": "IDENTITY_BRAINSTORMING",
                "identity_focus": "PASSIONS",
                "who_you_are": ["Curious Explorer"],
                "who_you_want_to_be": ["Visionary Leader"],
                "skipped_identity_categories": ["PASSIONS"],
                "current_identity": None,
                "proposed_identity": None,
                "metadata": {"foo": "bar"},
            },
            "identities": [
                {
                    "name": "Curious Explorer",
                    "category": "PASSIONS",
                    "state": "ACCEPTED",
                    "i_am_statement": "I am curious.",
                    "visualization": "A vivid scene.",
                    "notes": ["note1", "note2"],
                }
            ],
            "chat_messages": [
                {"role": "USER", "content": "I'm ready to brainstorm new identities."}
            ],
            "user_notes": [{"note": "User is highly motivated at this stage."}],
        }
        errors = validate_scenario_template(template)
        self.assertEqual(errors, [])

    def test_missing_required_field_in_user(self):
        """last_name is required — omitting it should produce a validation error."""
        template = {**VALID_TEMPLATE, "user": {"first_name": "Test"}}
        errors = validate_scenario_template(template)
        self.assertTrue(
            any(e["section"] == "user" and "last_name" in e["error"] for e in errors)
        )

    def test_extra_field_in_identity(self):
        template = VALID_TEMPLATE.copy()
        template["identities"] = [
            {
                "name": "Curious Explorer",
                "category": "PASSIONS",
                "state": "ACCEPTED",
                "foo": "bar",
            }
        ]
        errors = validate_scenario_template(template)
        self.assertTrue(
            any(
                e["section"].startswith("identity") and "foo" in e["error"]
                for e in errors
            )
        )

    def test_type_mismatch_in_coach_state(self):
        template = VALID_TEMPLATE.copy()
        template["coach_state"] = {
            **template["coach_state"],
            "who_you_are": "NotAList",
        }
        errors = validate_scenario_template(template)
        self.assertTrue(
            any(
                e["section"] == "coach_state" and "who_you_are" in e["error"]
                for e in errors
            )
        )

    def test_empty_sections_are_handled(self):
        template = VALID_TEMPLATE.copy()
        template["identities"] = []
        template["chat_messages"] = []
        template["user_notes"] = []
        errors = validate_scenario_template(template)
        self.assertEqual(errors, [])

    def test_null_user_section_is_error(self):
        template = VALID_TEMPLATE.copy()
        template["user"] = None
        errors = validate_scenario_template(template)
        self.assertTrue(
            any(e["section"] == "user" and "missing" in e["error"] for e in errors)
        )

    def test_missing_optional_sections_passes(self):
        template = VALID_TEMPLATE.copy()
        template.pop("coach_state")
        template.pop("identities")
        template.pop("chat_messages")
        template.pop("user_notes")
        errors = validate_scenario_template(template)
        self.assertEqual(errors, [])

    def test_minimal_valid_template_passes(self):
        errors = validate_scenario_template(MINIMAL_VALID_TEMPLATE)
        self.assertEqual(errors, [])

    # ==================== Coaching Phase Videos (PR 111) ====================

    def test_shown_videos_field_validates(self):
        """coach_state.shown_videos accepts a list of strings."""
        template = VALID_TEMPLATE.copy()
        template["coach_state"] = {
            **template["coach_state"],
            "shown_videos": ["welcome_session_intro", "get_to_know_session_intro"],
        }
        errors = validate_scenario_template(template)
        self.assertEqual(errors, [])

    def test_breaks_section_validates(self):
        """A well-formed breaks section is accepted."""
        template = VALID_TEMPLATE.copy()
        template["breaks"] = [
            {"triggered_by_session": "get_to_know_session"},
            {
                "triggered_by_session": "brainstorming_session",
                "ended_at": "2025-01-01T12:00:00Z",
                "original_coach_message_id": "abc-123",
            },
        ]
        errors = validate_scenario_template(template)
        self.assertEqual(errors, [])

    def test_extra_field_in_break(self):
        """Unknown fields in a break entry trigger the ForbidExtraFields mixin."""
        template = VALID_TEMPLATE.copy()
        template["breaks"] = [
            {"triggered_by_session": "get_to_know_session", "foo": "bar"},
        ]
        errors = validate_scenario_template(template)
        self.assertTrue(
            any(
                e["section"].startswith("break") and "foo" in e["error"]
                for e in errors
            )
        )

    def test_missing_required_field_in_break(self):
        """Omitting triggered_by_session produces a validation error."""
        template = VALID_TEMPLATE.copy()
        template["breaks"] = [{"ended_at": "2025-01-01T12:00:00Z"}]
        errors = validate_scenario_template(template)
        self.assertTrue(
            any(
                e["section"].startswith("break")
                and "triggered_by_session" in e["error"]
                for e in errors
            )
        )
