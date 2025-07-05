# Testing Implementation Plan: Template-Based Test Scenarios

## Overview

This document outlines the plan for implementing a robust, backend-driven, template-based test scenario system for the Discovita Dev Coach. The goal is to enable easy creation, editing, resetting, and management of test user states for comprehensive chatbot testing, especially as new coaching phases and features are added.

---

## Rationale & Requirements

- **Test scenarios** must capture the full state of a user (CoachState, Identities, ChatMessages, UserNotes, and User itself) at any point in the coaching journey.
- **Resettable:** Scenarios can be reset to their original state for repeated testing.
- **Editable:** Scenarios should be easy to update, both via backend and (optionally) frontend UI.
- **Trackable:** All test data must be clearly associated with its scenario for easy cleanup and isolation from real user data.
- **Backend-driven:** Test state management is handled on the backend, not the frontend.
- **Extensible:** The system should support new fields and models as the app evolves.
- **Admin UI First:** The first priority is to build an admin-facing UI for managing test scenarios (list, view, edit, create). The feature to capture a live user's state as a scenario will be implemented last.

---

## Approach: Template-Based Scenarios

### Why Templates?
- **Editability:** Easy to update scenarios, support for UI-driven editing.
- **Schema resilience:** Less risk of breakage if models change.
- **Partial updates:** Can update only parts of a scenario.
- **Composability:** Scenarios can be built from reusable templates.
- **Sufficient for most testing needs:** Exact reproducibility is not required.

---

## Data Model Changes

### 1. `TestScenario` Model
- **Fields:**
  - `id` (UUID, PK)
  - `name` (unique, for selection)
  - `description` (for UI)
  - `template` (JSONField, stores the declarative template)
  - `created_at`, `updated_at`
  - *(Optional)* `created_by` (FK to User)
- **Implementation Note:**
  - ✅ Model created with all required fields and docstrings. See `server/apps/test_scenario/models.py`.

### 2. Add `test_scenario` FK to All Relevant Models
- **Models updated:**
  - `User`
  - `CoachState`
  - `Identity`
  - `ChatMessage`
  - `UserNote`
- **Purpose:**
  - Groups all test data for a scenario
  - Enables easy filtering, reset, and deletion
- **Implementation Note:**
  - ✅ Added nullable `test_scenario` ForeignKey to all relevant models.
  - Used string reference `'test_scenario.TestScenario'` for the FK to avoid circular import issues. This was necessary for successful implementation and is a best practice in Django when models are interdependent.

---

## Template Structure

A scenario template is a JSON object describing the initial state for all relevant models. Example:

```json
{
  "user": {
    "email": "test_identity_brainstorming@example.com",
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
```

---

## Scenario Management Logic

- **Create Scenario:** Parse the template and create all related objects, linking them via the `test_scenario` FK.
- **Reset Scenario:** Delete all objects with the scenario FK, then re-run the template to re-create them.
- **Edit Scenario:** Update the template, then reset to apply changes.
- **Delete Scenario:** Delete all related objects and the scenario itself.

---

## Robust Template Validation & Schema Drift Handling

- The `template` field is a JSON object that must match the structure and required fields of the current backend models (User, CoachState, Identity, ChatMessage, UserNote).
- **Backend Validation:**
  - On scenario creation or edit, the backend will validate the template against the current model serializers.
  - If the template is missing required fields, has extra/invalid fields, or otherwise does not match the schema, the backend will return clear, actionable error messages.
  - Example errors:
    - "Missing required field: `current_phase` in `coach_state`."
    - "Unknown field: `foo` in `identity`."
- **Frontend Error Display:**
  - The admin UI will display these errors in a user-friendly way, with instructions for fixing them.
- **Future Versioning:**
  - (Optional, for future) Store a `schema_version` in the template for future migrations and compatibility checks.

---

## API Endpoints (Django Rest Framework ViewSet)

- `POST /api/test-scenarios/` — Create a new scenario from a template (with validation).
- `GET /api/test-scenarios/` — List all scenarios.
- `GET /api/test-scenarios/{id}/` — Get scenario details.
- `PUT/PATCH /api/test-scenarios/{id}/` — Update scenario/template (with validation).
- `POST /api/test-scenarios/{id}/reset/` — Reset scenario to template.
- `DELETE /api/test-scenarios/{id}/` — Delete scenario and all related data.
- *(To be implemented last)*: Endpoint to capture a live user's state as a new scenario (name TBD, not "freeze").

---

## Frontend Integration

- **Admin Test Scenario Management Page:**
  - List all test scenarios.
  - View/edit a scenario (with live validation feedback).
  - Create a new scenario.
  - Display backend validation errors in a user-friendly way.
- *(To be implemented last)*: UI for capturing a live user's state as a scenario.

---

## Extensibility & Best Practices

- **Add new fields to templates as models evolve.**
- **Support partial updates:** Only update the part of the scenario you want to change.
- **UI-driven scenario creation/editing:** Build forms that map directly to the template structure.
- **All test data is isolated by the `test_scenario` FK.**
- **Graceful error handling:** Always provide clear, actionable feedback if a template is invalid.
- **(Optional) Versioning:** Consider storing a `schema_version` in each template for future compatibility.

---

## Open Questions / Future Enhancements

- Should we support scenario versioning/history?
- Should we allow importing/exporting templates for sharing?
- How should we handle schema migrations for templates if models change significantly?
- What should we call the feature that captures a live user's state as a scenario? ("Freeze" is not descriptive enough.)

---

## Next Steps / TODO Checklist

- [x] Create the `TestScenario` model (with JSONField for template)
  - Implementation note: Model created with all required fields and docstrings.
- [x] Add `test_scenario` FK to all relevant models
  - Implementation note: Used string reference for FK to avoid circular import issues.
- [ ] Implement robust backend validation for scenario templates (with clear error messages)
- [ ] Build DRF viewset for scenario management (CRUD, reset, validation)
- [ ] Build admin frontend page for test scenario management (list, view, edit, create, show errors)
- [ ] (Optional) Add schema versioning to templates
- [ ] (Last) Implement feature to capture a live user's state as a scenario (name TBD)

---

**This document is a living reference. Update as implementation progresses!** 