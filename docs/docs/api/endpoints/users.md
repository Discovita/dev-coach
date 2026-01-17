# Users

## Base URL

`/users/`

---

## Endpoints

### 1. Get Current User Profile

- **URL:** `/users/me/`
- **Method:** `GET`
- **Description:** Returns the current authenticated user's profile data.
- **Authentication:** Required
- **Response:**
  - `200 OK`: User profile object.

#### Example Response

```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_superuser": false,
  "is_staff": false,
  "last_login": "2024-06-01T12:00:00Z",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-06-01T12:00:00Z",
  "groups": [],
  "user_permissions": [],
  "gender": "man",
  "skin_tone": "medium",
  "hair_color": "brown",
  "eye_color": "blue",
  "height": "average",
  "build": "athletic",
  "age_range": "thirties"
}
```

---

### 2. Get Complete User Data

- **URL:** `/users/me/complete/`
- **Method:** `GET`
- **Description:** Returns current user data and ensures chat history contains the initial bot message if empty.
- **Authentication:** Required
- **Response:**
  - `200 OK`: Complete user object with chat history initialized.

#### Example Response

```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_superuser": false,
  "is_staff": false,
  "last_login": "2024-06-01T12:00:00Z",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-06-01T12:00:00Z",
  "groups": [],
  "user_permissions": [],
  "gender": "man",
  "skin_tone": "medium",
  "hair_color": "brown",
  "eye_color": "blue",
  "height": "average",
  "build": "athletic",
  "age_range": "thirties",
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

### 3. Get User's Coach State

- **URL:** `/users/me/coach-state/`
- **Method:** `GET`
- **Description:** Returns the authenticated user's current coach state.
- **Authentication:** Required
- **Response:**
  - `200 OK`: Coach state object.
  - `404 Not Found`: If the user doesn't have a coach state.

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

### 4. Get User's Identities

- **URL:** `/users/me/identities/`
- **Method:** `GET`
- **Description:** Returns all identities associated with the authenticated user.
- **Authentication:** Required
- **Response:**
  - `200 OK`: Array of identity objects.

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

### 5. Get User's Actions

- **URL:** `/users/me/actions/`
- **Method:** `GET`
- **Description:** Returns all actions performed by the authenticated user, ordered by most recent first.
- **Authentication:** Required
- **Response:**
  - `200 OK`: Array of action objects.

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
    "test_scenario": null
  },
  {
    "id": "uuid-string",
    "user": "user-uuid",
    "action_type": "CREATE_IDENTITY",
    "action_type_display": "Create Identity",
    "parameters": {
      "identity_name": "Creative Visionary",
      "category": "PASSIONS"
    },
    "result_summary": "Created new identity: Creative Visionary",
    "timestamp": "2024-06-01T11:00:00Z",
    "timestamp_formatted": "2024-06-01 11:00:00",
    "coach_message": {
      "id": "uuid-string",
      "role": "COACH",
      "content": "I've created a new identity for you...",
      "timestamp": "2024-06-01T11:00:00Z"
    },
    "test_scenario": null
  }
]
```

---

### 6. Get User's Chat Messages

- **URL:** `/users/me/chat-messages/`
- **Method:** `GET`
- **Description:** Returns the authenticated user's chat messages. If the chat history is empty, adds the initial bot message and returns it. Returns the 20 most recent messages in chronological order.
- **Authentication:** Required
- **Response:**
  - `200 OK`: Array of chat message objects.

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

### 7. Reset User Data

- **URL:** `/users/me/reset-chat-messages/`
- **Method:** `POST`
- **Description:** Resets (deletes) all chat messages, identities, user notes, and actions for the authenticated user, and resets their CoachState to initial values. Adds the initial bot message back to the chat history if available.
- **Authentication:** Required
- **Response:**
  - `200 OK`: Array of chat message objects ordered by newest first (containing only the initial message if one was added).

#### Example Response

```json
[
  {
    "id": "uuid-string",
    "role": "COACH",
    "content": "Welcome to Dev Coach! I'm here to help you...",
    "timestamp": "2024-06-01T12:00:00Z"
  }
]
```

**Note:** If no initial message is configured, the response will be an empty array `[]`.

---

## Field Reference

For detailed field information on models returned by these endpoints, see:

- **[User Fields](../../database/models/users)** - Fields returned in user profile responses
- **[Coach State Fields](../../database/models/coach-state)** - Fields returned in coach state responses
- **[Identity Fields](../../database/models/identity)** - Fields returned in identity responses
- **[Action Fields](../../database/models/action)** - Fields returned in action responses
- **[Chat Message Fields](../../database/models/chat-message)** - Fields returned in chat message responses

---

## Notes

- All endpoints require authentication. See the authentication documentation for details.
- The `/users/me/complete/` endpoint automatically initializes chat history if empty.
- The `/users/me/chat-messages/` endpoint returns the 20 most recent messages in chronological order.
- The `/users/me/reset-chat-messages/` endpoint performs a complete reset of user data and should be used with caution.
- Test scenario endpoints require admin/superuser privileges and are used for test data management.
- Field values for enums must match the choices defined in their respective enum files:
  - `current_phase`: see `enums/coaching_phase.py`
  - `identity_focus`: see `enums/identity_category.py`
  - `action_type`: see `enums/action_type.py`
  - `role`: see `enums/message_role.py`
  - `state`: see `enums/identity_state.py`
  - `gender`: see `enums/appearance/gender.py`
  - `skin_tone`: see `enums/appearance/skin_tone.py`
  - `hair_color`: see `enums/appearance/hair_color.py`
  - `eye_color`: see `enums/appearance/eye_color.py`
  - `height`: see `enums/appearance/height.py`
  - `build`: see `enums/appearance/build.py`
  - `age_range`: see `enums/appearance/age_range.py`
- Appearance preference fields (`gender`, `skin_tone`, `hair_color`, `eye_color`, `height`, `build`, `age_range`) are optional and used for image generation visualization. These fields can be updated via PATCH requests to user endpoints.
- Update this document whenever the API changes.
