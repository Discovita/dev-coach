# Test Scenario System: Architecture, Implementation & Admin Tools

## Overview

This document provides a comprehensive overview of the Discovita Dev Coach test scenario system, combining the original implementation plan, backend model/API details, and the latest frontend admin tooling—including the dual coach state visualizer. It is intended as a living reference for developers and QA, and as onboarding for future maintainers.

---

## 1. Rationale & Requirements

- **Test scenarios** must capture the full state of a user (CoachState, Identities, ChatMessages, UserNotes, and User itself) at any point in the coaching journey.
- **Resettable:** Scenarios can be reset to their original state for repeated testing.
- **Editable:** Scenarios should be easy to update, both via backend and (optionally) frontend UI.
- **Trackable:** All test data must be clearly associated with its scenario for easy cleanup and isolation from real user data.
- **Backend-driven:** Test state management is handled on the backend, not the frontend.
- **Extensible:** The system should support new fields and models as the app evolves.
- **Admin UI First:** The first priority is to build an admin-facing UI for managing test scenarios (list, view, edit, create). The feature to capture a live user's state as a scenario will be implemented last.

---

## 2. Backend: Data Model & API

### 2.1 TestScenario Model
- **Fields:**
  - `id` (UUID, PK)
  - `name` (unique, for selection)
  - `description` (for UI)
  - `template` (JSONField, stores the declarative template)
  - `created_at`, `updated_at`
  - *(Optional)* `created_by` (FK to User)
- **Implementation Note:**
  - Model created with all required fields and docstrings. See `server/apps/test_scenario/models.py`.

### 2.2 Template Structure
A scenario template is a JSON object describing the initial state for all relevant models. Example:

```json
{
  "user": { ... },
  "coach_state": { ... },
  "identities": [ ... ],
  "chat_messages": [ ... ],
  "user_notes": [ ... ]
}
```

### 2.3 Foreign Keys for Isolation
- All relevant models (`User`, `CoachState`, `Identity`, `ChatMessage`, `UserNote`) have a nullable `test_scenario` FK for grouping and cleanup.

### 2.4 Scenario Management Logic
- **Create:** Parse the template and create all related objects, linking them via the `test_scenario` FK.
- **Reset:** Delete all objects with the scenario FK, then re-run the template to re-create them.
- **Edit:** Update the template, then reset to apply changes.
- **Delete:** Delete all related objects and the scenario itself.

### 2.5 Robust Template Validation
- Uses DRF serializers for each section (User, CoachState, Identity, ChatMessage, UserNote).
- Forbids extra/unknown fields, provides actionable error messages.
- Validation is run on create and update.
- Comprehensive tests ensure reliability.

### 2.6 API Endpoints
- `POST /api/test-scenarios/` — Create a new scenario from a template (with validation).
- `GET /api/test-scenarios/` — List all scenarios.
- `GET /api/test-scenarios/{id}/` — Get scenario details.
- `PUT/PATCH /api/test-scenarios/{id}/` — Update scenario/template (with validation).
- `POST /api/test-scenarios/{id}/reset/` — Reset scenario to template.
- `DELETE /api/test-scenarios/{id}/` — Delete scenario and all related data.
- *(To be implemented last)*: Endpoint to capture a live user's state as a new scenario.

---

## 3. Admin Tools & Frontend Architecture

### 3.1 Test Scenario Admin Endpoints
- **ViewSet:** `TestUserViewSet` provides admin/superuser-only endpoints for fetching and managing test scenario user data.
- **Endpoints:**
  - `/api/v1/test-user/{user_id}/profile/` — Get test user profile
  - `/api/v1/test-user/{user_id}/complete/` — Get all test user data (chat, coach state, etc.)
  - `/api/v1/test-user/{user_id}/coach-state/` — Get coach state
  - `/api/v1/test-user/{user_id}/identities/` — Get identities
  - `/api/v1/test-user/{user_id}/chat-messages/` — Get chat messages
- **Permissions:** Only admin/superuser can access these endpoints.
- **Purpose:** Enables admins to simulate any test user for scenario-based QA and debugging.

### 3.2 Admin-Only Chat & Impersonation
- **Endpoint:** `/api/v1/coach/process-message-for-user/`
  - Allows an admin to send a chat message as any user (by user_id).
  - Uses the same business logic as the regular chat endpoint, but impersonates the specified user.
- **Security:** Only admin/superuser can use this endpoint.
- **Use Case:** Enables full test scenario chat simulation without logging in/out or switching users.

### 3.3 Frontend: Test Scenario UI & Hooks
- **Hooks Directory:** `client/src/hooks/test-scenario/`
- **Hooks Implemented:**
  - `useTestScenarioUserChatMessages` — Fetch/send chat messages (with optimistic UI)
  - `useTestScenarioUserCoachState` — Fetch coach state
  - `useTestScenarioUserIdentities` — Fetch identities
  - `useTestScenarioUserActions` — Get actions from cache
  - `useTestScenarioUserFinalPrompt` — Get final prompt from cache
- **API Parity:** All hooks mirror the main user hooks for easy UI reuse and maintenance.

### 3.4 Dual Coach State Visualizer (Frontend)
- **Problem:** The original Coach State Visualizer always used the authenticated user's data, even in test scenario mode.
- **Solution:** There are now two visualizer components:
  - `CoachStateVisualizer` — Uses only user hooks, for the authenticated/admin user.
  - `TestScenarioCoachStateVisualizer` — Uses only test-scenario hooks, for test scenario users (requires `testUserId`).
- **Tab Content:**
  - `TabContent` — For user mode, uses user hooks.
  - `TestScenarioTabContent` — For test scenario mode, uses test-scenario hooks and requires `testUserId`.
- **UI Logic:** The parent component (`TestChat`) renders the correct visualizer and tab content based on whether a test scenario is active.
- **Result:** The correct data is always shown, and only the relevant hooks are called, preventing stale or incorrect state.

### 3.5 Admin UI Features
- **Test Scenario Table:** List, edit, create, and delete scenarios.
- **TestChat:** Lets admins launch a chat as any test user or resume their own session.
- **Visual Feedback:** The UI clearly distinguishes between test scenario and admin sessions.
- **Optimistic UI:** Chat messages and state update instantly for a smooth QA experience.

---

## 4. Best Practices & Maintenance

- **Keep test user endpoints and hooks in sync with main user features for best UX.**
- **When adding new coach state fields or features, update both user and test-scenario hooks/components.**
- **Use the provided docs and scripts for onboarding and troubleshooting.**
- **Write comprehensive tests for backend validation and scenario management.**
- **Document any changes to the template schema or API endpoints.**
- **If you add new tabs or data to the visualizer, update both TabContent and TestScenarioTabContent.**

---

## 5. Open Questions / Future Enhancements

- Should we support scenario versioning/history?
- Should we allow importing/exporting templates for sharing?
- How should we handle schema migrations for templates if models change significantly?
- What should we call the feature that captures a live user's state as a scenario? ("Freeze" is not descriptive enough.)

---

**For questions or further improvements, see the code comments or ask the dev team!** 