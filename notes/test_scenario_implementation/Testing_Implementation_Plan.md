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

## Implementation Progress & Notes

### **Key Decisions & Lessons Learned**
- **Template Serializers:** Created dedicated serializers for each section (User, CoachState, Identity, ChatMessage, UserNote) that strictly match the fields required for scenario creation. These serializers:
  - Forbid extra/unknown fields (using a mixin)
  - Provide actionable error messages (including field names)
  - Are the canonical schema for scenario templates
- **Validation Logic:** Updated to use the template serializers, ensuring robust, actionable validation for all template input.
- **Test Suite:** Comprehensive tests for template validation are in place and all are passing. These tests cover:
  - Valid templates
  - Missing required fields
  - Extra/invalid fields
  - Type mismatches
  - Edge cases (empty sections, nulls, etc.)
- **Error Handling:** Error messages now include field names, making them much more actionable for both developers and UI users.
- **Strictness:** The system now strictly enforces template schema, which will prevent subtle bugs and make future UI/automation work much more reliable.

### **Current Status**
- [x] Template serializers implemented and in sync with creation logic
- [x] Validation logic updated to use template serializers
- [x] All validation tests passing (robust coverage)
- [x] Extra fields are now forbidden and reported clearly
- [x] Error messages are actionable and field-specific
- [x] **TestUserViewSet and all admin endpoints for fetching test user data (profile, complete, coach state, identities, chat messages) are implemented and documented.**

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
  - `name` (unique, for selection) (this should have some sort of structure: e.g. created_by_name:title)
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

## Validation Implementation Plan

### Goals
- Ensure scenario templates match the current schema for all relevant models (`User`, `CoachState`, `Identity`, `ChatMessage`, `UserNote`).
- Catch missing required fields, extra/invalid fields, and type mismatches.
- Provide clear, actionable error messages to the admin user.
- Make validation reusable for both creation and update of scenarios.

### Approach
- **Use Django REST Framework (DRF) Serializers:**
  - For each section of the template (`user`, `coach_state`, `identities`, `chat_messages`, `user_notes`), use the corresponding DRF serializer (or a custom one if needed).
  - Validate the data as if it were being used to create a model instance (but don't actually save).
- **Validation Flow:**
  1. Parse the `template` JSON.
  2. For each section:
     - Pass the data to the appropriate serializer with `data=...`.
     - Call `is_valid()`.
     - Collect any errors.
  3. If any errors are found, return a 400 response with a structured list of errors, e.g.:
     ```json
     {
       "errors": [
         {"section": "user", "error": "Missing required field: email"},
         {"section": "coach_state", "error": "Unknown field: foo"}
       ]
     }
     ```
  4. If all sections are valid, allow the scenario to be created/updated.
- **Error Messaging:**
  - Errors should be section-specific (e.g., "user", "identity[0]").
  - Human-readable and actionable (e.g., "Missing required field: current_phase in coach_state").
  - Optionally, include suggestions for fixing the error.
- **Extensibility:**
  - If models change, updating the serializers will automatically update the validation logic.
  - If new sections are added to the template, add corresponding validation.
- **(Optional) Schema Versioning:**
  - If you add a `schema_version` field to the template, you can provide version-specific validation in the future.

### Testing
- **Write comprehensive tests for the validation logic before using it in production.**
  - Tests should cover:
    - Valid templates (should pass)
    - Templates missing required fields (should fail with clear errors)
    - Templates with extra/invalid fields (should fail with clear errors)
    - Type mismatches (should fail with clear errors)
    - Edge cases (empty sections, nulls, etc.)
- **Tests will ensure the validation is robust and reliable before enabling scenario management in the UI.**

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

## New Feature: Capture ("Freeze") Current User Session as Test Scenario

### Overview

Enable an admin to capture ("freeze") the current state of any user session (including chat messages, identities, coach state, user notes, and user profile) and create a new test scenario from it. This feature is admin-only, accessible from the `TestChat.tsx` component, and will streamline QA and scenario creation.

### Requirements

- **Admin-only:** Feature is only available to admin users.
- **Accessible from TestChat:** UI is in `TestChat.tsx` (for both admin’s own session and test scenario sessions).
- **Data to Capture:** All relevant user state: `User`, `CoachState`, `Identity`, `ChatMessage`, `UserNote`.
- **Form Input:** Admin provides a unique scenario name and description.
- **Backend:** New API endpoint to accept user ID, name, and description, and generate a new `TestScenario` with a template built from the user’s current state.
- **Validation:** Name must be unique; backend validates and returns actionable errors.
- **Extensibility:** Solution should be robust to future model/template changes.

### Backend Implementation

- **New API Endpoint:**
  - **Location:** `server/apps/test_scenario/views.py` (in `TestScenarioViewSet`)
  - **Route:** `POST /api/test-scenarios/freeze-session/`
  - **Permissions:** `IsAdminUser`
  - **Input:** `{ user_id, name, description }`
  - **Output:** Created `TestScenario` object (or error)

- **Logic:**
  1. **Validate input:** Ensure `user_id` exists, `name` is unique, and required fields are present.
  2. **Gather user state:** Query all relevant models for the given user:
     - `User`
     - `CoachState`
     - `Identity` (all for user)
     - `ChatMessage` (all for user)
     - `UserNote` (all for user)
     
     **Note:** The backend already provides robust admin-only endpoints for fetching all required user state via the `TestUserViewSet` (see `test_user_api.md`). These can be leveraged for the freeze-session feature.
  3. **Build template JSON:** Structure as per the canonical template schema.
  4. **Create new `TestScenario`:** Save with the generated template, name, and description.
  5. **(Optional) Instantiate scenario:** Use existing logic if immediate instantiation is desired.
  6. **Return:** The created scenario or a structured error.

- **Validation & Error Handling:**
  - Use DRF serializers for template validation (as in existing scenario creation).
  - Return clear, actionable error messages for:
    - Duplicate name
    - Invalid/missing user
    - Schema mismatches

### Frontend Implementation

- **UI/UX in `TestChat.tsx`:**
  - **Button:** “Create Test Scenario from Current Session” (admin-only)
  - **Modal/Form:** For entering scenario name and description
  - **API Call:** On submit, send `{ user_id, name, description }` to new endpoint
  - **Feedback:** Show loading, success, and error states
  - **Update UI:** Optionally refresh scenario list or show a link to the new scenario

- **Data Handling:**
  - **user_id:**  
    - If in test scenario mode: use `testUserId`
    - If in admin mode: use current user’s ID (from auth context/hook)
  - **Form validation:** Ensure name/description are not empty before submit

- **Comments & Documentation:**
  - Add step-by-step comments at the top of the handler/component
  - Inline comments for non-obvious logic

### Testing & Validation

- **Backend:**  
  - Unit tests for endpoint (valid/invalid input, edge cases)
  - Manual test: create scenario from both admin and test user sessions
- **Frontend:**  
  - Manual test: create scenario, handle errors, see new scenario in list
  - (Optional) Add Cypress or React Testing Library tests for UI

### Documentation

- Update relevant markdown docs:
  - `test_scenario_system_overview.md`
  - `Testing_Implementation_Plan.md`
  - `test_scenario_admin_tools_overview.md`
- Document new endpoint, UI, and any changes to the template schema

### Edge Cases & Future-Proofing

- **Large sessions:** Consider pagination/limits if user has many messages/notes
- **Schema drift:** Use DRF serializers for template validation to ensure future compatibility
- **Extensibility:** If new models are added, update both the backend data gathering and the template schema

---

## Next Steps / TODO Checklist

- [x] Create the `TestScenario` model (with JSONField for template)
  - Implementation note: Model created with all required fields and docstrings.
- [x] Add `test_scenario` FK to all relevant models
  - Implementation note: Used string reference for FK to avoid circular import issues.
- [x] Implement robust backend validation for scenario templates (with clear error messages)
- [x] Write and pass comprehensive tests for scenario template validation
- [x] Build DRF viewset for scenario management (CRUD, reset, validation)
- [x] Build admin backend endpoints for test user data (TestUserViewSet: profile, complete, coach state, identities, chat messages)
- [ ] Build admin frontend page for test scenario management (list, view, edit, create, show errors)
- [ ] (Optional) Add schema versioning to templates
- [x] (Last) Implement feature to capture a live user's state as a scenario (see section above)
- [ ] Implement new freeze-session endpoint in `TestScenarioViewSet`
- [ ] Add/extend serializers and tests for freeze-session
- [ ] Add button, modal, and API integration in `TestChat.tsx`
- [ ] Add UI feedback and error handling for freeze-session
- [ ] Update markdown docs and API docs for freeze-session
- [ ] Manual and automated tests for end-to-end freeze-session flow

---

**This document is a living reference. Update as implementation progresses!** 