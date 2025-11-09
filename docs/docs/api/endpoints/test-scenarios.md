# Test Scenarios

## Base URL

`/test-scenarios/`

---

## Overview

The TestScenarioViewSet provides admin-only endpoints for creating, managing, and manipulating test scenarios. Test scenarios are complete snapshots of user coaching sessions that can be instantiated and reset for testing purposes. Each scenario includes user data, coach state, identities, chat messages, user notes, and actions.

**Important**: All endpoints require admin/superuser privileges.

---

## Endpoints

### 1. List Test Scenarios

- **URL:** `/test-scenarios/`
- **Method:** `GET`
- **Description:** List all test scenarios in the system.
- **Authentication:** Required (Admin/Superuser only)
- **Response:**
  - `200 OK`: Array of test scenario objects.

#### Example Response

```json
[
  {
    "id": "uuid-string",
    "name": "Basic Introduction Flow",
    "description": "A simple test scenario for the introduction phase",
    "template": {
      "user": {
        "id": "user-uuid",
        "email": "test_user_abc123@testscenario.com",
        "password": "Coach123!",
        "first_name": "Test",
        "last_name": "User"
      }
    },
    "created_by": "admin@example.com",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-06-01T12:00:00Z"
  }
]
```

---

### 2. Retrieve Test Scenario

- **URL:** `/test-scenarios/{id}/`
- **Method:** `GET`
- **Description:** Retrieve a specific test scenario by ID.
- **Authentication:** Required (Admin/Superuser only)
- **Response:**
  - `200 OK`: Test scenario object.
  - `404 Not Found`: Scenario not found.

#### Example Response

```json
{
  "id": "uuid-string",
  "name": "Complete Coaching Session",
  "description": "A full coaching session with multiple phases and identities",
  "template": {
    "user": {
      "id": "user-uuid",
      "email": "test_user_abc123@testscenario.com",
      "password": "Coach123!",
      "first_name": "John",
      "last_name": "Doe"
    },
    "coach_state": {
      "current_phase": "IDENTITY_CREATION",
      "identity_focus": "PASSIONS",
      "who_you_are": ["Creative", "Determined"],
      "who_you_want_to_be": ["Successful", "Inspiring"]
    },
    "identities": [
      {
        "name": "Creative Visionary",
        "category": "PASSIONS",
        "state": "ACCEPTED",
        "i_am_statement": "I am a bold creator, transforming ideas into reality.",
        "visualization": "I see myself confidently presenting innovative solutions...",
        "notes": ["Note 1", "Note 2"]
      }
    ],
    "chat_messages": [
      {
        "role": "COACH",
        "content": "Welcome to Dev Coach! I'm here to help you...",
        "timestamp": "2024-06-01T12:00:00Z"
      },
      {
        "role": "USER",
        "content": "Hi! I'm excited to start this journey.",
        "timestamp": "2024-06-01T12:01:00Z"
      }
    ],
    "user_notes": [
      {
        "note": "User shows strong creative tendencies",
        "source_message": "message-uuid",
        "created_at": "2024-06-01T12:05:00Z"
      }
    ],
    "actions": [
      {
        "action_type": "TRANSITION_PHASE",
        "parameters": {
          "from_phase": "INTRODUCTION",
          "to_phase": "GET_TO_KNOW_YOU"
        },
        "result_summary": "Successfully transitioned from Introduction to Get To Know You phase",
        "timestamp": "2024-06-01T12:02:00Z",
        "coach_message_content": "Great! Let's move to the next phase..."
      }
    ]
  },
  "created_by": "admin@example.com",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-06-01T12:00:00Z"
}
```

---

### 3. Create Test Scenario

- **URL:** `/test-scenarios/`
- **Method:** `POST`
- **Description:** Create a new test scenario with a complete template. The scenario will be automatically instantiated with all related data.
- **Authentication:** Required (Admin/Superuser only)
- **Request Body:**
  ```json
  {
    "name": "New Test Scenario",
    "description": "A test scenario for development",
    "template": {
      "user": {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com"
      },
      "coach_state": {
        "current_phase": "INTRODUCTION",
        "identity_focus": "PASSIONS",
        "who_you_are": [],
        "who_you_want_to_be": []
      }
    }
  }
  ```
- **Response:**
  - `201 Created`: Created test scenario object.
  - `400 Bad Request`: Validation errors in template.

#### Example Response

Same format as the retrieve endpoint.

---

### 4. Update Test Scenario

- **URL:** `/test-scenarios/{id}/`
- **Method:** `PUT`
- **Description:** Update an existing test scenario. The scenario will be re-instantiated with the new template data.
- **Authentication:** Required (Admin/Superuser only)
- **Request Body:**
  ```json
  {
    "name": "Updated Test Scenario",
    "description": "Updated description",
    "template": {
      "user": {
        "first_name": "Updated",
        "last_name": "User",
        "email": "updated@example.com"
      },
      "coach_state": {
        "current_phase": "GET_TO_KNOW_YOU",
        "identity_focus": "PASSIONS",
        "who_you_are": ["Creative"],
        "who_you_want_to_be": ["Successful"]
      }
    }
  }
  ```
- **Response:**
  - `200 OK`: Updated test scenario object.
  - `400 Bad Request`: Validation errors.
  - `404 Not Found`: Scenario not found.

---

### 5. Delete Test Scenario

- **URL:** `/test-scenarios/{id}/`
- **Method:** `DELETE`
- **Description:** Permanently delete a test scenario and all associated data.
- **Authentication:** Required (Admin/Superuser only)
- **Response:**
  - `200 OK`: Success message.
  - `404 Not Found`: Scenario not found.

#### Example Response

```json
{
  "success": true,
  "message": "Test scenario deleted successfully."
}
```

---

### 6. Reset Test Scenario

- **URL:** `/test-scenarios/{id}/reset/`
- **Method:** `POST`
- **Description:** Reset a test scenario to its original template state. This will delete all current instantiated data and recreate it from the template.
- **Authentication:** Required (Admin/Superuser only)
- **Response:**
  - `200 OK`: Success message.

#### Example Response

```json
{
  "success": true,
  "message": "Scenario reset (all data)."
}
```

---

### 7. Freeze Session

- **URL:** `/test-scenarios/freeze-session/`
- **Method:** `POST`
- **Description:** Capture the current state of a user session as a new test scenario. This creates a complete snapshot of a user's coaching session.
- **Authentication:** Required (Admin/Superuser only)
- **Request Body:**
  ```json
  {
    "user_id": "user-uuid",
    "name": "Frozen Session - John Doe",
    "description": "Snapshot of John's coaching session",
    "first_name": "John",
    "last_name": "Doe"
  }
  ```
- **Response:**
  - `201 Created`: Created test scenario object.
  - `400 Bad Request`: Validation errors or missing fields.
  - `403 Forbidden`: Not authorized.
  - `404 Not Found`: User not found.

#### Example Response

Same format as the retrieve endpoint.

---

## Template Schema

### Required Sections

#### User Section

```json
{
  "user": {
    "first_name": "string (required)",
    "last_name": "string (required)",
    "email": "string (optional, auto-generated if not unique)",
    "password": "string (optional, always set to 'Coach123!')",
    "is_active": "boolean (optional)",
    "is_superuser": "boolean (optional)",
    "is_staff": "boolean (optional)",
    "verification_token": "string (optional)",
    "email_verification_sent_at": "datetime (optional)"
  }
}
```

### Optional Sections

#### Coach State Section

```json
{
  "coach_state": {
    "current_phase": "string (required)",
    "identity_focus": "string (required)",
    "who_you_are": ["string array (required)"],
    "who_you_want_to_be": ["string array (required)"],
    "asked_questions": ["string array (optional)"],
    "skipped_identity_categories": ["string array (optional)"],
    "proposed_identity": "string (optional)",
    "current_identity": "string (optional)",
    "metadata": "object (optional)"
  }
}
```

#### Identities Section

```json
{
  "identities": [
    {
      "name": "string (required)",
      "category": "string (required)",
      "state": "string (optional)",
      "i_am_statement": "string (optional)",
      "visualization": "string (optional)",
      "notes": ["string array (optional)"]
    }
  ]
}
```

#### Chat Messages Section

```json
{
  "chat_messages": [
    {
      "role": "string (required)",
      "content": "string (required)",
      "timestamp": "datetime (optional)"
    }
  ]
}
```

#### User Notes Section

```json
{
  "user_notes": [
    {
      "note": "string (required)",
      "source_message": "string (optional)",
      "created_at": "datetime (optional)"
    }
  ]
}
```

#### Actions Section

```json
{
  "actions": [
    {
      "action_type": "string (required)",
      "parameters": "object (required)",
      "result_summary": "string (optional)",
      "timestamp": "datetime (optional)",
      "coach_message_content": "string (optional)"
    }
  ]
}
```

---

## Use Cases

### Development and Testing

- **Feature Testing**: Create scenarios to test new coaching features
- **Regression Testing**: Maintain scenarios to ensure existing functionality works
- **Edge Case Testing**: Create scenarios with unusual data combinations

### Quality Assurance

- **Session Reproduction**: Freeze real user sessions for bug investigation
- **Data Validation**: Verify coaching flows work with specific data sets
- **Performance Testing**: Test system performance with realistic data volumes

---

## Field Reference

For detailed field information on models used in these endpoints, see:

- **[Test Scenario Fields](../../database/models/test-scenario)** - Test scenario model structure
- **[User Fields](../../database/models/users)** - User model structure
- **[Coach State Fields](../../database/models/coach-state)** - Coach state structure
- **[Identity Fields](../../database/models/identity)** - Identity model structure
- **[Chat Message Fields](../../database/models/chat-message)** - Chat message structure
- **[Action Fields](../../database/models/action)** - Action model structure

---

## Notes

- All endpoints require admin/superuser privileges for security.
- Template validation is strict - only defined fields are allowed. The freeze-session endpoint ensures the correct structure as well as the create and update endpoints. These are all used on the front end on the Test page available to Admins.
- Scenario instantiation creates all related database objects automatically.
- The freeze-session endpoint captures complete user state for scenario creation.
- Test users are automatically assigned unique emails if conflicts exist.
- All test users have the password "Coach123!" for consistency.
- Scenario reset completely recreates all related data from the template.
