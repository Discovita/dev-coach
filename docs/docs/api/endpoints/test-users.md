# Test Users

## Base URL

`/api/v1/admin/test-user`

---

## Overview

The AdminTestUserViewSet provides admin-only endpoints for accessing and managing user data. These endpoints mirror the functionality of the regular UserViewSet but allow admin users to access data for specific users by ID, making them essential for testing, debugging, and scenario management. Also includes a list-all endpoint for admin impersonation UI.

**Important**: All endpoints require IsAdminUser permission (is_staff OR is_superuser).

---

## Endpoints

### 1. List All Users

- **URL:** `/api/v1/admin/test-user/all`
- **Method:** `GET`
- **Description:** List all users with basic info. Used by admin impersonation UI to browse and select a user to view as. Returns lightweight user objects (no nested identities/messages). Includes test_scenario info so the UI can distinguish real vs test users.
- **Authentication:** Required (IsAdminUser — is_staff OR is_superuser)
- **Response:**
  - `200 OK`: Array of lightweight user objects.

#### Example Response

```json
[
  {
    "id": "uuid-string",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "is_staff": false,
    "is_superuser": false,
    "last_login": "2024-06-01T12:00:00Z",
    "created_at": "2024-01-01T12:00:00Z",
    "coaching_phase": "introduction",
    "is_test_user": false,
    "test_scenario_name": null
  },
  {
    "id": "uuid-string-2",
    "email": "test_user_abc@testscenario.com",
    "first_name": "Test",
    "last_name": "User",
    "is_active": true,
    "is_staff": false,
    "is_superuser": false,
    "last_login": null,
    "created_at": "2024-02-01T12:00:00Z",
    "coaching_phase": "identity_brainstorming",
    "is_test_user": true,
    "test_scenario_name": "Basic Introduction Flow"
  }
]
```

---

### 2. Get Test User Profile

- **URL:** `/api/v1/admin/test-user/{pk}/profile`
- **Method:** `GET`
- **Description:** Get profile data for a specific user.
- **Authentication:** Required (IsAdminUser — is_staff OR is_superuser)
- **Response:**
  - `200 OK`: User profile object.
  - `404 Not Found`: User not found.

#### Example Response

```json
{
  "id": "uuid-string",
  "email": "testuser@example.com",
  "first_name": "Test",
  "last_name": "User",
  "is_active": true,
  "is_superuser": false,
  "is_staff": false,
  "last_login": "2024-06-01T12:00:00Z",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-06-01T12:00:00Z",
  "groups": [],
  "user_permissions": []
}
```

---

### 3. Update Test User Profile (Partial)

- **URL:** `/api/v1/admin/test-user/{pk}/update-profile`
- **Method:** `PATCH`
- **Description:** Partially update a user's profile. Only the provided fields are updated.
- **Authentication:** Required (IsAdminUser — is_staff OR is_superuser)
- **Request Body:**
  ```json
  {
    "first_name": "Updated",
    "gender": "man"
  }
  ```
- **Response:**
  - `200 OK`: Updated user profile object.
  - `400 Bad Request`: Validation errors.
  - `404 Not Found`: User not found.

---

### 4. Get Test User Complete Data

- **URL:** `/api/v1/admin/test-user/{pk}/complete`
- **Method:** `GET`
- **Description:** Get complete data for a user, ensuring the chat history contains the initial bot message if empty.
- **Authentication:** Required (IsAdminUser — is_staff OR is_superuser)
- **Response:**
  - `200 OK`: Complete user object with chat history initialized.
  - `404 Not Found`: User not found.

#### Example Response

```json
{
  "id": "uuid-string",
  "email": "testuser@example.com",
  "first_name": "Test",
  "last_name": "User",
  "is_active": true,
  "is_superuser": false,
  "is_staff": false,
  "last_login": "2024-06-01T12:00:00Z",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-06-01T12:00:00Z",
  "groups": [],
  "user_permissions": [],
  "identities": [
    {
      "id": "uuid-string",
      "user": "user-uuid",
      "name": "Creative Visionary",
      "i_am_statement": "I am a bold creator, transforming ideas into reality.",
      "visualization": "I see myself confidently presenting innovative solutions...",
      "state": "accepted",
      "notes": ["Note 1", "Note 2"],
      "category": "passions_and_talents",
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-06-01T12:00:00Z"
    }
  ],
  "coach_state": {
    "id": "uuid-string",
    "user": "user-uuid",
    "current_phase": "introduction",
    "current_identity": null,
    "proposed_identity": null,
    "identity_focus": "passions_and_talents",
    "skipped_identity_categories": [],
    "who_you_are": [],
    "who_you_want_to_be": [],
    "asked_questions": [],
    "updated_at": "2024-06-01T12:00:00Z"
  },
  "chat_messages": [
    {
      "id": "uuid-string",
      "role": "coach",
      "content": "Welcome to Dev Coach! I'm here to help you...",
      "timestamp": "2024-06-01T12:00:00Z",
      "component_config": null
    }
  ]
}
```

---

### 5. Get Test User Coach State

- **URL:** `/api/v1/admin/test-user/{pk}/coach-state`
- **Method:** `GET`
- **Description:** Get the coach state for a user.
- **Authentication:** Required (IsAdminUser — is_staff OR is_superuser)
- **Response:**
  - `200 OK`: Coach state object.
  - `404 Not Found`: User or coach state not found.

#### Example Response

```json
{
  "id": "uuid-string",
  "user": "user-uuid",
  "current_phase": "introduction",
  "current_identity": null,
  "proposed_identity": null,
  "identity_focus": "passions_and_talents",
  "skipped_identity_categories": [],
  "who_you_are": [],
  "who_you_want_to_be": [],
  "asked_questions": [],
  "updated_at": "2024-06-01T12:00:00Z"
}
```

---

### 6. Get Test User Identities

- **URL:** `/api/v1/admin/test-user/{pk}/identities`
- **Method:** `GET`
- **Description:** Get the identities for a user. Supports archive filtering via query params.
- **Authentication:** Required (IsAdminUser — is_staff OR is_superuser)
- **Query Parameters:**
  - `include_archived` (optional): Set to `true` to include archived identities. Default: `false`
  - `archived_only` (optional): Set to `true` to return only archived identities. Default: `false`
- **Response:**
  - `200 OK`: Array of identity objects.
  - `404 Not Found`: User not found.

#### Example Response

```json
[
  {
    "id": "uuid-string",
    "user": "user-uuid",
    "name": "Creative Visionary",
    "i_am_statement": "I am a bold creator, transforming ideas into reality.",
    "visualization": "I see myself confidently presenting innovative solutions...",
    "state": "accepted",
    "notes": ["Note 1", "Note 2"],
    "category": "passions_and_talents",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-06-01T12:00:00Z"
  },
  {
    "id": "uuid-string",
    "user": "user-uuid",
    "name": "Warrior",
    "i_am_statement": "I treat my body with strength, discipline, and respect.",
    "visualization": "I see myself in peak physical condition...",
    "state": "accepted",
    "notes": [],
    "category": "physical_expression",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-06-01T12:00:00Z"
  }
]
```

---

### 7. Get Test User Actions

- **URL:** `/api/v1/admin/test-user/{pk}/actions`
- **Method:** `GET`
- **Description:** Get the actions for a user, ordered by most recent first.
- **Authentication:** Required (IsAdminUser — is_staff OR is_superuser)
- **Response:**
  - `200 OK`: Array of action objects.
  - `404 Not Found`: User not found.

#### Example Response

```json
[
  {
    "id": "uuid-string",
    "user": "user-uuid",
    "action_type": "transition_phase",
    "action_type_display": "Transition Phase",
    "parameters": {
      "from_phase": "introduction",
      "to_phase": "get_to_know_you"
    },
    "result_summary": "Successfully transitioned from Introduction to Get To Know You phase",
    "timestamp": "2024-06-01T12:00:00Z",
    "updated_at": "2024-06-01T12:00:00Z",
    "timestamp_formatted": "2024-06-01 12:00:00",
    "coach_message": {
      "id": "uuid-string",
      "role": "coach",
      "content": "Great! Let's move to the next phase...",
      "timestamp": "2024-06-01T12:00:00Z",
      "component_config": null
    },
    "test_scenario": "scenario-uuid"
  }
]
```

---

### 8. Get Test User Chat Messages

- **URL:** `/api/v1/admin/test-user/{pk}/chat-messages`
- **Method:** `GET`
- **Description:** Get all chat messages for a user in chronological order. If the chat history is empty, adds the initial bot message and returns it.
- **Authentication:** Required (IsAdminUser — is_staff OR is_superuser)
- **Response:**
  - `200 OK`: Array of chat message objects.
  - `404 Not Found`: User not found.

#### Example Response

```json
[
  {
    "id": "uuid-string",
    "role": "coach",
    "content": "Welcome to Dev Coach! I'm here to help you...",
    "timestamp": "2024-06-01T12:00:00Z",
    "component_config": null
  },
  {
    "id": "uuid-string",
    "role": "user",
    "content": "Hi! I'm excited to start this journey.",
    "timestamp": "2024-06-01T12:01:00Z",
    "component_config": null
  },
  {
    "id": "uuid-string",
    "role": "coach",
    "content": "Wonderful! I'm so excited to start this journey with you...",
    "timestamp": "2024-06-01T12:01:30Z",
    "component_config": null
  }
]
```

---

## Use Cases

### Testing and Debugging
- **Scenario Testing**: Access specific test user data to verify coaching flows
- **Debugging**: Inspect user state, actions, and chat history for troubleshooting
- **Development**: Test new features with specific user scenarios

### Test Scenario Management
- **Data Inspection**: View complete user data including identities and coach state
- **State Verification**: Check coaching phase progression and identity development
- **Action Tracking**: Monitor actions performed during coaching sessions

### Admin Tools
- **User Monitoring**: Track test user progress and coaching session state
- **Data Validation**: Verify test scenario data integrity
- **Performance Analysis**: Analyze coaching session effectiveness

---

## Field Reference

For detailed field information on models used in these endpoints, see:

- **[User Fields](../../database/models/users)** - User model fields and structure
- **[Coach State Fields](../../database/models/coach-state)** - Coach state structure
- **[Identity Fields](../../database/models/identity)** - Identity model structure
- **[Action Fields](../../database/models/action)** - Action model structure
- **[Chat Message Fields](../../database/models/chat-message)** - Chat message structure

---

## Notes

- All endpoints require IsAdminUser permission (is_staff OR is_superuser).
- The resource is registered as `test-user` on the admin router, so all paths use `/api/v1/admin/test-user/...`.
- These endpoints mirror the regular UserViewSet functionality but operate on specific users by PK.
- The `/all` endpoint returns lightweight user objects without nested identities/messages for the admin impersonation UI.
- Test scenario users are typically created as part of test scenario instantiation.
- The endpoints automatically handle initial message creation for empty chat histories.
- All enum values in responses use lowercase stored values (e.g., `"introduction"` not `"INTRODUCTION"`).
- Actions are ordered by timestamp (most recent first) for easy analysis.
- These endpoints are essential for test scenario management and debugging.
- Update this document whenever the API changes.
