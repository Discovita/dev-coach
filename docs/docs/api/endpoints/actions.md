# Actions

## Base URL

`/actions/`

---

## Overview

The ActionViewSet provides read-only access to coaching actions performed by the system. Actions represent the operations that the coach performs during coaching sessions, such as creating identities, transitioning phases, or updating user data. This endpoint is primarily used for admin interfaces, action history tracking, and conversation reconstruction.

**Important**: All endpoints require authentication. Regular users can only see their own actions, while admin users can see all actions.

---

## Endpoints

### 1. List Actions

- **URL:** `/actions/`
- **Method:** `GET`
- **Description:** List actions with optional filtering. Regular users see only their own actions, while admin users see all actions.
- **Authentication:** Required
- **Query Parameters:**
  - `action_type` (optional): Filter by specific action type
  - `user` (optional): Filter by user ID (admin only)
  - `test_scenario` (optional): Filter by test scenario ID (admin only)
- **Response:**
  - `200 OK`: Array of action objects (simplified list format).

#### Example Response

```json
[
  {
    "id": "uuid-string",
    "action_type": "CREATE_IDENTITY",
    "action_type_display": "Create Identity",
    "result_summary": "Created new identity 'Creative Visionary' in PASSIONS category",
    "timestamp": "2024-06-01T12:00:00Z",
    "coach_message_preview": "I've created a new identity for you based on our conversation..."
  },
  {
    "id": "uuid-string-2",
    "action_type": "TRANSITION_PHASE",
    "action_type_display": "Transition Phase",
    "result_summary": "Transitioned from INTRODUCTION to GET_TO_KNOW_YOU phase",
    "timestamp": "2024-06-01T11:55:00Z",
    "coach_message_preview": "Great! Now let's move to the next phase of our coaching..."
  }
]
```

---

### 2. Retrieve Action

- **URL:** `/actions/{id}/`
- **Method:** `GET`
- **Description:** Retrieve a specific action with full details including the related coach message.
- **Authentication:** Required
- **Response:**
  - `200 OK`: Action object with complete details.
  - `404 Not Found`: Action not found or not accessible.

#### Example Response

```json
{
  "id": "uuid-string",
  "user": "user-uuid",
  "action_type": "CREATE_IDENTITY",
  "action_type_display": "Create Identity",
  "parameters": {
    "identity_name": "Creative Visionary",
    "category": "PASSIONS",
    "i_am_statement": "I am a bold creator, transforming ideas into reality.",
    "visualization": "I see myself confidently presenting innovative solutions to complex problems, inspiring others with my creative vision."
  },
  "result_summary": "Created new identity 'Creative Visionary' in PASSIONS category with 'I Am' statement and visualization",
  "timestamp": "2024-06-01T12:00:00Z",
  "timestamp_formatted": "2024-06-01 12:00:00",
  "coach_message": {
    "id": "message-uuid",
    "user": "user-uuid",
    "role": "COACH",
    "content": "Based on our conversation about your creative projects and passion for innovation, I've created a new identity for you: 'Creative Visionary'. This identity captures your ability to see possibilities where others see obstacles. Your 'I Am' statement is: 'I am a bold creator, transforming ideas into reality.' And your visualization is: 'I see myself confidently presenting innovative solutions to complex problems, inspiring others with my creative vision.' How does this identity resonate with you?",
    "timestamp": "2024-06-01T12:00:00Z"
  },
  "test_scenario": null
}
```

---

### 3. Get Actions for User (Admin Only)

- **URL:** `/actions/for-user/`
- **Method:** `GET`
- **Description:** Get all actions for a specific user. Admin users only.
- **Authentication:** Required (Admin/Superuser only)
- **Query Parameters:**
  - `user_id` (required): ID of the user whose actions to retrieve
- **Response:**
  - `200 OK`: Array of action objects for the specified user.
  - `400 Bad Request`: Missing user_id parameter.
  - `403 Forbidden`: Not authorized (non-admin user).
  - `404 Not Found`: User not found.

#### Example Request

```
GET /actions/for-user/?user_id=123
```

#### Example Response

```json
[
  {
    "id": "uuid-string",
    "action_type": "CREATE_IDENTITY",
    "action_type_display": "Create Identity",
    "parameters": {
      "identity_name": "Creative Visionary",
      "category": "PASSIONS"
    },
    "result_summary": "Created new identity 'Creative Visionary' in PASSIONS category",
    "timestamp": "2024-06-01T12:00:00Z",
    "timestamp_formatted": "2024-06-01 12:00:00",
    "coach_message": {
      "id": "message-uuid",
      "user": "123",
      "role": "COACH",
      "content": "Based on our conversation...",
      "timestamp": "2024-06-01T12:00:00Z"
    },
    "test_scenario": null
  }
]
```

---

### 4. Get Actions by Coach Message

- **URL:** `/actions/by-coach-message/`
- **Method:** `GET`
- **Description:** Get all actions triggered by a specific coach message. Users can only see actions for their own messages unless they are admin.
- **Authentication:** Required
- **Query Parameters:**
  - `message_id` (required): ID of the coach message
- **Response:**
  - `200 OK`: Array of action objects triggered by the message.
  - `400 Bad Request`: Missing message_id parameter.
  - `403 Forbidden`: Not authorized to view actions for this message.
  - `404 Not Found`: Message not found.

#### Example Request

```
GET /actions/by-coach-message/?message_id=456
```

#### Example Response

```json
[
  {
    "id": "uuid-string",
    "action_type": "CREATE_IDENTITY",
    "action_type_display": "Create Identity",
    "parameters": {
      "identity_name": "Creative Visionary",
      "category": "PASSIONS"
    },
    "result_summary": "Created new identity 'Creative Visionary' in PASSIONS category",
    "timestamp": "2024-06-01T12:00:00Z",
    "timestamp_formatted": "2024-06-01 12:00:00",
    "coach_message": {
      "id": "456",
      "user": "user-uuid",
      "role": "COACH",
      "content": "Based on our conversation...",
      "timestamp": "2024-06-01T12:00:00Z"
    },
    "test_scenario": null
  }
]
```

---

## Action Types

The system supports various action types that represent different coaching operations:

### Common Action Types

- **`CREATE_IDENTITY`**: Creates a new identity for the user
- **`UPDATE_IDENTITY`**: Updates an existing identity
- **`TRANSITION_PHASE`**: Moves the coaching session to a new phase
- **`CREATE_USER_NOTE`**: Creates a note about the user
- **`UPDATE_COACH_STATE`**: Updates the user's coaching state
- **`SKIP_IDENTITY_CATEGORY`**: Marks an identity category as skipped

### Action Parameters

Each action type has specific parameters that define what the action does:

#### CREATE_IDENTITY Parameters

```json
{
  "identity_name": "string",
  "category": "string",
  "i_am_statement": "string (optional)",
  "visualization": "string (optional)"
}
```

#### TRANSITION_PHASE Parameters

```json
{
  "from_phase": "string",
  "to_phase": "string"
}
```

#### UPDATE_IDENTITY Parameters

```json
{
  "identity_id": "string",
  "field_name": "string",
  "new_value": "string"
}
```

---

## Use Cases

### Admin Interface

- **Action History**: View all actions performed by the system
- **User Investigation**: Examine specific user's coaching journey
- **System Monitoring**: Track coaching system performance and usage

### Debugging and Development

- **Conversation Reconstruction**: Understand what actions were triggered by specific messages
- **Action Validation**: Verify that actions are being performed correctly
- **Test Scenario Analysis**: Examine actions in test scenarios

### User Experience

- **Progress Tracking**: Users can see what actions have been performed on their behalf
- **Transparency**: Understand what the coaching system is doing
- **Accountability**: Track coaching system decisions and actions

---

## Field Reference

For detailed field information on models used in these endpoints, see:

- **[Action Fields](/docs/database/models/action)** - Action model structure
- **[Chat Message Fields](/docs/database/models/chat-message)** - Chat message structure
- **[User Fields](/docs/database/models/users)** - User model structure

---

## Notes

- All endpoints require authentication.
- Regular users can only see their own actions.
- Admin users can see all actions and use the `for-user` endpoint.
- Actions are ordered by timestamp (newest first) in list responses.
- The `by-coach-message` endpoint helps trace which actions were triggered by specific coach messages.
- Action parameters are stored as JSON and validated to ensure they are objects.
- Actions can only be linked to coach messages, not user messages.
- The list endpoint uses a simplified serializer to reduce response size.
- Update this document whenever the API changes.
