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

### 2. Add `test_scenario` FK to All Relevant Models
- **Models to update:**
  - `User`
  - `CoachState`
  - `Identity`
  - `ChatMessage`
  - `UserNote`
- **Purpose:**
  - Groups all test data for a scenario
  - Enables easy filtering, reset, and deletion

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

## API Endpoints (Django Rest Framework ViewSet)

- `POST /api/test-scenarios/` — Create a new scenario from a template.
- `GET /api/test-scenarios/` — List all scenarios.
- `GET /api/test-scenarios/{id}/` — Get scenario details.
- `PUT/PATCH /api/test-scenarios/{id}/` — Update scenario/template.
- `POST /api/test-scenarios/{id}/reset/` — Reset scenario to template.
- `DELETE /api/test-scenarios/{id}/` — Delete scenario and all related data.

---

## Frontend Integration

- **TestStateSelector** and related UI will fetch scenarios from the backend.
- UI for editing templates (optional, but recommended for future flexibility).
- Trigger reset, edit, and delete via API.

---

## Extensibility & Best Practices

- **Add new fields to templates as models evolve.**
- **Support partial updates:** Only update the part of the scenario you want to change.
- **UI-driven scenario creation/editing:** Build forms that map directly to the template structure.
- **All test data is isolated by the `test_scenario` FK.**

---

## Open Questions / Future Enhancements

- Should we support scenario versioning/history?
- Should we allow importing/exporting templates for sharing?
- How should we handle schema migrations for templates if models change significantly?

---

## Next Steps / TODO Checklist

- [ ] Update models to add `test_scenario` FK
- [ ] Create the `TestScenario` model
- [ ] Implement scenario creation/reset logic (template parser/runner)
- [ ] Build DRF viewset for scenario management
- [ ] Update frontend to use backend-driven scenarios
- [ ] (Optional) Build UI for editing templates

---

**This document is a living reference. Update as implementation progresses!** 