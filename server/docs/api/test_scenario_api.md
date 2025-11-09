# Test Scenario System: API & Developer Reference

---

## 1. TestScenarioViewSet API Documentation

This section documents the main endpoints for managing test scenarios, as implemented in `views.py`.

### Permissions
- All endpoints require admin/superuser privileges (`IsAdminUser`).

### Endpoints

#### 1. List All Test Scenarios
- **URL:** `/api/v1/test-scenarios`
- **Method:** `GET`
- **Description:** Returns a list of all test scenarios.
- **Response Example:**
```json
[
  {
    "id": "...",
    "name": "Identity Brainstorming",
    "description": "Test scenario for identity brainstorming phase.",
    "template": { ... },
    ...
  },
  ...
]
```

#### 2. Create a New Test Scenario
- **URL:** `/api/v1/test-scenarios`
- **Method:** `POST`
- **Description:** Creates a new test scenario from a template. Validates the template strictly.
- **Request Example:**
```json
{
  "name": "My Test Scenario",
  "description": "Testing user creation and all related data",
  "template": { ... }
}
```
- **Response:** The created scenario object, or validation errors.

#### 3. Retrieve a Test Scenario
- **URL:** `/api/v1/test-scenarios/{id}`
- **Method:** `GET`
- **Description:** Returns details for a specific test scenario.

#### 4. Update a Test Scenario
- **URL:** `/api/v1/test-scenarios/{id}`
- **Method:** `PUT` or `PATCH`
- **Description:** Updates a scenario's name, description, or template. Validates the template.

#### 5. Delete a Test Scenario
- **URL:** `/api/v1/test-scenarios/{id}`
- **Method:** `DELETE`
- **Description:** Deletes the scenario and all related test data.

#### 6. Reset a Test Scenario
- **URL:** `/api/v1/test-scenarios/{id}/reset`
- **Method:** `POST`
- **Description:** Resets the scenario to its original template state (deletes and recreates all related data).
- **Response Example:**
```json
{
  "success": true,
  "message": "Scenario reset (all data)."
}
```

#### 7. Freeze a Live User Session as a Test Scenario
- **URL:** `/api/v1/test-scenarios/freeze-session`
- **Method:** `POST`
- **Description:** Captures the current state of a user session as a new test scenario. Accepts user_id, name, description, first_name, last_name.
- **Request Example:**
```json
{
  "user_id": "...",
  "name": "Frozen Session",
  "description": "Snapshot of user state.",
  "first_name": "Casey",
  "last_name": "Smith"
}
```
- **Response:** The created scenario object, or validation errors.

---

## 2. Template Serializers Reference (`template_serializers.py`)

These serializers define the strict schema for each section of a test scenario template. They are used for validation and documentation.

### TemplateUserSerializer
- **Fields:**
  - `email` (optional, unique or auto-generated)
  - `first_name` (required)
  - `last_name` (required)
  - `is_active`, `is_superuser`, `is_staff` (optional)
  - `verification_token`, `email_verification_sent_at` (optional)
- **Purpose:** Ensures user data in templates matches the expected schema for test user creation.

### TemplateCoachStateSerializer
- **Fields:**
  - `current_phase` (required)
  - `identity_focus` (required)
  - `who_you_are`, `who_you_want_to_be` (required, list)
  - `skipped_identity_categories`, `current_identity`, `proposed_identity`, `metadata` (optional)

### TemplateIdentitySerializer
- **Fields:**
  - `name`, `category` (required)
  - `state`, `i_am_statement`, `visualization`, `notes` (optional)

### TemplateChatMessageSerializer
- **Fields:**
  - `role`, `content` (required)
  - `timestamp` (optional)

### TemplateUserNoteSerializer
- **Fields:**
  - `note` (required)
  - `source_message`, `created_at` (optional)

### ForbidExtraFieldsMixin
- **Purpose:** Any extra/unknown fields in a template section will cause validation to fail, ensuring strict schema adherence.

---

## 3. Scenario Instantiation Service (`services.py`)

The `instantiate_test_scenario` function is responsible for creating all related test data from a scenario template. It is used on scenario creation, reset, and freeze.

### Function: instantiate_test_scenario
- **Arguments:**
  - `scenario`: The TestScenario instance
  - `create_user`, `create_chat_messages`, `create_identities`, `create_coach_state`, `create_user_notes`: Booleans to control which sections to instantiate
- **Step-by-step:**
  1. Deletes any existing test user(s) for the scenario
  2. Creates a new test user from the template (with a unique email if needed)
  3. Creates/updates the CoachState for the user
  4. Creates all Identities, ChatMessages, and UserNotes for the user
- **Password:** Always sets the test user's password to `Coach123!`
- **Isolation:** All created objects are linked to the scenario via the `test_scenario` FK
- **Return Value:** Dict with references to created user, coach state, and email

---

## 4. Error Handling & Validation

- All endpoints return actionable error messages for missing/invalid fields, unknown fields, or schema mismatches.
- Validation is enforced both on the backend (via serializers) and on the frontend (via form validation and error display).

---

**For further details, see the code comments in each file or contact the dev team.** 