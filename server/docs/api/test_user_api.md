# TestUserViewSet API Documentation

This document describes the API endpoints for the `TestUserViewSet`, which provides admin-only access to test scenario user data. All endpoints require admin or superuser privileges and operate on a specific user by user id (`pk`).

**Base URL:** `/api/v1/test-user/`

---

## Permissions
- All endpoints require authentication (`IsAuthenticated`).
- Only users with `is_staff` or `is_superuser` may access these endpoints.

---

## Endpoints

### 1. Get Test User Profile
- **URL:** `/api/v1/test-user/{user_id}/profile/`
- **Method:** `GET`
- **Description:** Returns the profile data for the specified test user.
- **Response Example:**
```json
{
  "id": 123,
  "email": "testuser@example.com",
  "first_name": "Test",
  "last_name": "User",
  ...
}
```

---

### 2. Get Complete Test User Data
- **URL:** `/api/v1/test-user/{user_id}/complete/`
- **Method:** `GET`
- **Description:** Returns all data for the specified test user, ensuring the initial bot message exists in chat history.
- **Response Example:**
```json
{
  "id": 123,
  "email": "testuser@example.com",
  "first_name": "Test",
  "last_name": "User",
  "coach_state": { ... },
  "identities": [ ... ],
  "chat_messages": [ ... ],
  ...
}
```

---

### 3. Get Test User Coach State
- **URL:** `/api/v1/test-user/{user_id}/coach-state/`
- **Method:** `GET`
- **Description:** Returns the coach state for the specified test user.
- **Response Example:**
```json
{
  "current_phase": "INTRODUCTION",
  "identity_focus": "PASSIONS",
  ...
}
```

---

### 4. Get Test User Identities
- **URL:** `/api/v1/test-user/{user_id}/identities/`
- **Method:** `GET`
- **Description:** Returns the list of identities for the specified test user.
- **Response Example:**
```json
[
  {
    "name": "Leader",
    "category": "CAREER",
    ...
  },
  ...
]
```

---

### 5. Get Test User Chat Messages
- **URL:** `/api/v1/test-user/{user_id}/chat-messages/`
- **Method:** `GET`
- **Description:** Returns the chat messages for the specified test user. If the chat history is empty, the initial bot message is added and returned.
- **Response Example:**
```json
[
  {
    "role": "coach",
    "content": "Welcome to your coaching session!",
    "timestamp": "2024-07-04T12:00:00Z"
  },
  ...
]
```

---

## Error Responses
- `403 Forbidden`: Returned if the authenticated user is not an admin or superuser.
- `404 Not Found`: Returned if the specified user does not exist.

---

## Notes
- All endpoints require a valid user id (`user_id`) as a path parameter.
- These endpoints are intended for test scenario and admin tooling only.
- All data returned is for the specified user, not the currently authenticated user. 