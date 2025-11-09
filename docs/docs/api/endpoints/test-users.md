# Test Users

## Base URL

`/users/`

---

## Overview

The TestUserViewSet provides admin-only endpoints for accessing and managing test scenario user data. These endpoints mirror the functionality of the regular UserViewSet but allow admin users to access data for specific users by ID, making them essential for testing, debugging, and scenario management.

**Important**: All endpoints require admin/superuser privileges and a specific user ID in the URL path.

---

## Endpoints

### 1. Get Test User Profile

- **URL:** `/users/{user_id}/profile/`
- **Method:** `GET`
- **Description:** Get profile data for a specific test scenario user.
- **Authentication:** Required (Admin/Superuser only)
- **Response:**
  - `200 OK`: User profile object.
  - `403 Forbidden`: Not authorized (not admin/superuser).
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

### 2. Get Test User Complete Data

- **URL:** `/users/{user_id}/complete/`
- **Method:** `GET`
- **Description:** Get complete data for a test scenario user, ensuring the chat history contains the initial bot message if empty.
- **Authentication:** Required (Admin/Superuser only)
- **Response:**
  - `200 OK`: Complete user object with chat history initialized.
  - `403 Forbidden`: Not authorized (not admin/superuser).
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
      "state": "ACCEPTED",
      "notes": ["Note 1", "Note 2"],
      "category": "PASSIONS",
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-06-01T12:00:00Z"
    }
  ],
  "coach_state": {
    "id": "uuid-string",
    "user": "user-uuid",
    "current_phase": "INTRODUCTION",
    "current_identity": null,
    "proposed_identity": null,
    "identity_focus": "PASSIONS",
    "skipped_identity_categories": [],
    "who_you_are": [],
    "who_you_want_to_be": [],
    "asked_questions": [],
    "updated_at": "2024-06-01T12:00:00Z"
  },
  "chat_messages": [
    {
      "id": "uuid-string",
      "role": "COACH",
      "content": "Welcome to Dev Coach! I'm here to help you...",
      "timestamp": "2024-06-01T12:00:00Z"
    }
  ]
}
```

---

### 3. Get Test User Coach State

- **URL:** `/users/{user_id}/coach-state/`
- **Method:** `GET`
- **Description:** Get the coach state for a test scenario user.
- **Authentication:** Required (Admin/Superuser only)
- **Response:**
  - `200 OK`: Coach state object.
  - `403 Forbidden`: Not authorized (not admin/superuser).
  - `404 Not Found`: User or coach state not found.

#### Example Response

```json
{
  "id": "uuid-string",
  "user": "user-uuid",
  "current_phase": "INTRODUCTION",
  "current_identity": null,
  "proposed_identity": null,
  "identity_focus": "PASSIONS",
  "skipped_identity_categories": [],
  "who_you_are": [],
  "who_you_want_to_be": [],
  "asked_questions": [],
  "updated_at": "2024-06-01T12:00:00Z"
}
```

---

### 4. Get Test User Identities

- **URL:** `/users/{user_id}/identities/`
- **Method:** `GET`
- **Description:** Get the identities for a test scenario user.
- **Authentication:** Required (Admin/Superuser only)
- **Response:**
  - `200 OK`: Array of identity objects.
  - `403 Forbidden`: Not authorized (not admin/superuser).
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
    "state": "ACCEPTED",
    "notes": ["Note 1", "Note 2"],
    "category": "PASSIONS",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-06-01T12:00:00Z"
  },
  {
    "id": "uuid-string",
    "user": "user-uuid",
    "name": "Warrior",
    "i_am_statement": "I treat my body with strength, discipline, and respect.",
    "visualization": "I see myself in peak physical condition...",
    "state": "ACCEPTED",
    "notes": [],
    "category": "PHYSICAL_HEALTH",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-06-01T12:00:00Z"
  }
]
```

---

### 5. Get Test User Actions

- **URL:** `/users/{user_id}/actions/`
- **Method:** `GET`
- **Description:** Get the actions for a test scenario user, ordered by most recent first.
- **Authentication:** Required (Admin/Superuser only)
- **Response:**
  - `200 OK`: Array of action objects.
  - `403 Forbidden`: Not authorized (not admin/superuser).
  - `404 Not Found`: User not found.

#### Example Response

```json
[
  {
    "id": "uuid-string",
    "user": "user-uuid",
    "action_type": "TRANSITION_PHASE",
    "action_type_display": "Transition Phase",
    "parameters": {
      "from_phase": "INTRODUCTION",
      "to_phase": "GET_TO_KNOW_YOU"
    },
    "result_summary": "Successfully transitioned from Introduction to Get To Know You phase",
    "timestamp": "2024-06-01T12:00:00Z",
    "timestamp_formatted": "2024-06-01 12:00:00",
    "coach_message": {
      "id": "uuid-string",
      "role": "COACH",
      "content": "Great! Let's move to the next phase...",
      "timestamp": "2024-06-01T12:00:00Z"
    },
    "test_scenario": "scenario-uuid"
  }
]
```

---

### 6. Get Test User Chat Messages

- **URL:** `/users/{user_id}/chat-messages/`
- **Method:** `GET`
- **Description:** Get the chat messages for a test scenario user. If the chat history is empty, adds the initial bot message and returns it.
- **Authentication:** Required (Admin/Superuser only)
- **Response:**
  - `200 OK`: Array of chat message objects.
  - `403 Forbidden`: Not authorized (not admin/superuser).
  - `404 Not Found`: User not found.

#### Example Response

```json
[
  {
    "id": "uuid-string",
    "role": "COACH",
    "content": "Welcome to Dev Coach! I'm here to help you...",
    "timestamp": "2024-06-01T12:00:00Z"
  },
  {
    "id": "uuid-string",
    "role": "USER",
    "content": "Hi! I'm excited to start this journey.",
    "timestamp": "2024-06-01T12:01:00Z"
  },
  {
    "id": "uuid-string",
    "role": "COACH",
    "content": "Wonderful! I'm so excited to start this journey with you...",
    "timestamp": "2024-06-01T12:01:30Z"
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

- All endpoints require admin/superuser privileges for security.
- These endpoints mirror the regular UserViewSet functionality but operate on specific users by ID.
- Test scenario users are typically created as part of test scenario instantiation.
- The endpoints automatically handle initial message creation for empty chat histories.
- Actions are ordered by timestamp (most recent first) for easy analysis.
- These endpoints are essential for test scenario management and debugging.
- Update this document whenever the API changes.
