import pytest
pytestmark = pytest.mark.django_db
# Import the validation function and template serializers
from apps.test_scenario.validation import validate_scenario_template

"""
Test Suite: Scenario Template Validation
---------------------------------------
This suite tests the validation logic for test scenario templates.
Covers:
- Valid templates (should pass)
- Missing required fields (should fail)
- Extra/invalid fields (should fail)
- Type mismatches (should fail)
- Edge cases (empty sections, nulls, etc.)
- All optional fields present (should pass)

Each test asserts that the validation function returns the expected errors (or no errors) for a given template.
"""

# Example valid template (update fields as needed to match your template serializers)
VALID_TEMPLATE = {
    "user": {
        "email": "test@example.com",
        "password": "Coach123!",  # Required for test scenario users
        "first_name": "Test",
        "last_name": "User"
    },
    "coach_state": {
        "current_phase": "IDENTITY_BRAINSTORMING",
        "identity_focus": "PASSIONS",
        "who_you_are": ["Curious Explorer"],
        "who_you_want_to_be": ["Visionary Leader"]
    },
    "identities": [
        {
            "name": "Curious Explorer",
            "category": "PASSIONS",
            "state": "ACCEPTED"
        }
    ],
    "chat_messages": [
        {
            "role": "USER",
            "content": "I'm ready to brainstorm new identities."
        }
    ],
    "user_notes": [
        {
            "note": "User is highly motivated at this stage."
        }
    ]
}

# Minimal valid template (only user required)
MINIMAL_VALID_TEMPLATE = {
    "user": {
        "email": "test@example.com",
        "password": "Coach123!",
        "first_name": "Test",
        "last_name": "User"
    }
}


def test_valid_template_passes():
    """
    GIVEN a fully valid scenario template (with required fields only)
    WHEN it is validated
    THEN no errors should be returned
    """
    errors = validate_scenario_template(VALID_TEMPLATE)
    assert errors == []


def test_all_optional_fields_present():
    """
    GIVEN a template with all optional fields populated for each section
    WHEN it is validated
    THEN no errors should be returned
    """
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
            "email_verification_sent_at": "2024-01-01T00:00:00Z"
        },
        "coach_state": {
            "current_phase": "IDENTITY_BRAINSTORMING",
            "identity_focus": "PASSIONS",
            "who_you_are": ["Curious Explorer"],
            "who_you_want_to_be": ["Visionary Leader"],
            "skipped_identity_categories": ["PASSIONS"],
            "current_identity": None,
            "proposed_identity": None,
            "metadata": {"foo": "bar"}
        },
        "identities": [
            {
                "name": "Curious Explorer",
                "category": "PASSIONS",
                "state": "ACCEPTED",
                "affirmation": "I am curious.",
                "visualization": "A vivid scene.",
                "notes": ["note1", "note2"]
            }
        ],
        "chat_messages": [
            {
                "role": "USER",
                "content": "I'm ready to brainstorm new identities."
            }
        ],
        "user_notes": [
            {
                "note": "User is highly motivated at this stage."
            }
        ]
    }
    errors = validate_scenario_template(template)
    assert errors == []


def test_missing_required_field_in_user():
    """
    GIVEN a template missing a required field in the user section
    WHEN it is validated
    THEN an error about the missing field should be returned
    """
    template = {**VALID_TEMPLATE, "user": {"first_name": "Test"}}
    errors = validate_scenario_template(template)
    assert any(e["section"] == "user" and "email" in e["error"] for e in errors)


def test_extra_field_in_identity():
    """
    GIVEN a template with an extra/invalid field in an identity
    WHEN it is validated
    THEN an error about the unknown field should be returned
    """
    template = VALID_TEMPLATE.copy()
    template["identities"] = [
        {"name": "Curious Explorer", "category": "PASSIONS", "state": "ACCEPTED", "foo": "bar"}
    ]
    errors = validate_scenario_template(template)
    assert any(e["section"].startswith("identity") and "foo" in e["error"] for e in errors)


def test_type_mismatch_in_coach_state():
    """
    GIVEN a template with a type mismatch in coach_state (e.g., who_you_are is a string, not a list)
    WHEN it is validated
    THEN an error about the type mismatch should be returned
    """
    template = VALID_TEMPLATE.copy()
    template["coach_state"] = {**template["coach_state"], "who_you_are": "NotAList"}
    errors = validate_scenario_template(template)
    assert any(e["section"] == "coach_state" and "who_you_are" in e["error"] for e in errors)


def test_empty_sections_are_handled():
    """
    GIVEN a template with empty lists for identities, chat_messages, and user_notes
    WHEN it is validated
    THEN no errors should be returned (if empty is allowed)
    """
    template = VALID_TEMPLATE.copy()
    template["identities"] = []
    template["chat_messages"] = []
    template["user_notes"] = []
    errors = validate_scenario_template(template)
    assert errors == []


def test_null_section_is_error():
    """
    GIVEN a template with a null section (e.g., user is None)
    WHEN it is validated
    THEN an error about the missing section should be returned
    """
    template = VALID_TEMPLATE.copy()
    template["user"] = None
    errors = validate_scenario_template(template)
    assert any(e["section"] == "user" and "missing" in e["error"] for e in errors)


def test_missing_section_is_okay_for_optional_sections():
    """
    GIVEN a template missing an optional section (e.g., no coach_state)
    WHEN it is validated
    THEN no errors should be returned
    """
    template = VALID_TEMPLATE.copy()
    template.pop("coach_state")
    template.pop("identities")
    template.pop("chat_messages")
    template.pop("user_notes")
    errors = validate_scenario_template(template)
    assert errors == []


def test_minimal_valid_template_passes():
    """
    GIVEN a template with only the required user section
    WHEN it is validated
    THEN no errors should be returned
    """
    errors = validate_scenario_template(MINIMAL_VALID_TEMPLATE)
    assert errors == []

# Add more edge case tests as needed for your business logic 