# Prompts

## Base URL

`/prompts/`

---

## Endpoints

### 1. List Prompts

- **URL:** `/prompts/`
- **Method:** `GET`
- **Description:** List all active prompts (only those with `is_active=True`).
- **Authentication:** Required
- **Response:**
  - `200 OK`: Array of active prompt objects.

#### Example Response

```json
[
  {
    "id": "uuid-string",
    "coaching_phase": "INTRODUCTION",
    "version": 1,
    "name": "Welcome Message",
    "description": "Initial greeting for new users",
    "body": "Welcome to Dev Coach! I'm here to help you...",
    "required_context_keys": ["user_name", "coaching_phase"],
    "allowed_actions": ["TRANSITION_PHASE", "CREATE_IDENTITY"],
    "prompt_type": "COACH",
    "is_active": true,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-06-01T12:00:00Z"
  },
  {
    "id": "uuid-string",
    "coaching_phase": "GET_TO_KNOW_YOU",
    "version": 2,
    "name": "Question Flow",
    "description": "Asking questions to understand the user",
    "body": "Let me ask you a few questions to better understand...",
    "required_context_keys": ["user_name", "asked_questions"],
    "allowed_actions": ["UPDATE_WHO_YOU_ARE", "TRANSITION_PHASE"],
    "prompt_type": "COACH",
    "is_active": true,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-06-01T12:00:00Z"
  }
]
```

---

### 2. Retrieve Prompt

- **URL:** `/prompts/{id}/`
- **Method:** `GET`
- **Description:** Retrieve a single prompt by ID.
- **Authentication:** Required
- **Response:**
  - `200 OK`: Prompt object.
  - `404 Not Found`: If prompt doesn't exist.

#### Example Response

```json
{
  "id": "uuid-string",
  "coaching_phase": "INTRODUCTION",
  "version": 1,
  "name": "Welcome Message",
  "description": "Initial greeting for new users",
  "body": "Welcome to Dev Coach! I'm here to help you...",
  "required_context_keys": ["user_name", "coaching_phase"],
  "allowed_actions": ["TRANSITION_PHASE", "CREATE_IDENTITY"],
  "prompt_type": "COACH",
  "is_active": true,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-06-01T12:00:00Z"
}
```

---

### 3. Create Prompt

- **URL:** `/prompts/`
- **Method:** `POST`
- **Description:** Create a new prompt. Automatically assigns the next version number based on `prompt_type` and `coaching_phase`.
  - For prompts with `coaching_phase`: versions are unique per (`prompt_type`, `coaching_phase`)
  - For prompts without `coaching_phase` (e.g., `image_generation`, `sentinel`): versions are unique per `prompt_type`
- **Authentication:** Required
- **Request Body:**
  ```json
  {
    "coaching_phase": "INTRODUCTION",
    "name": "Welcome Message",
    "description": "Initial greeting for new users",
    "body": "Welcome to Dev Coach! I'm here to help you...",
    "required_context_keys": ["user_name", "coaching_phase"],
    "allowed_actions": ["TRANSITION_PHASE", "CREATE_IDENTITY"],
    "prompt_type": "COACH",
    "is_active": true
  }
  ```
  
  **Example for prompts without coaching_phase:**
  ```json
  {
    "coaching_phase": null,
    "name": "Identity Image Generation Prompt",
    "description": "Prompt for generating identity images",
    "body": "Create an image for this identity...",
    "required_context_keys": ["identity_for_image"],
    "allowed_actions": [],
    "prompt_type": "IMAGE_GENERATION",
    "is_active": true
  }
  ```
- **Response:**
  - `201 Created`: Created prompt object.
  - `400 Bad Request`: Validation errors.

#### Example Response

```json
{
  "id": "uuid-string",
  "coaching_phase": "INTRODUCTION",
  "version": 3,
  "name": "Welcome Message",
  "description": "Initial greeting for new users",
  "body": "Welcome to Dev Coach! I'm here to help you...",
  "required_context_keys": ["user_name", "coaching_phase"],
  "allowed_actions": ["TRANSITION_PHASE", "CREATE_IDENTITY"],
  "prompt_type": "COACH",
  "is_active": true,
  "created_at": "2024-06-01T12:00:00Z",
  "updated_at": "2024-06-01T12:00:00Z"
}
```

**Note:** The `version` field is automatically assigned and ignores any value sent from the frontend. Version numbers are unique per combination of `prompt_type`, `coaching_phase`, and `version`.

---

### 4. Update Prompt (Full Update)

- **URL:** `/prompts/{id}/`
- **Method:** `PUT`
- **Description:** Update a prompt with all fields (full update).
- **Authentication:** Required
- **Request Body:**
  ```json
  {
    "coaching_phase": "INTRODUCTION",
    "version": 1,
    "name": "Updated Welcome Message",
    "description": "Updated initial greeting for new users",
    "body": "Welcome to Dev Coach! I'm here to help you on your journey...",
    "required_context_keys": ["user_name", "coaching_phase", "user_goals"],
    "allowed_actions": [
      "TRANSITION_PHASE",
      "CREATE_IDENTITY",
      "UPDATE_WHO_YOU_ARE"
    ],
    "prompt_type": "COACH",
    "is_active": true
  }
  ```
- **Response:**
  - `200 OK`: Updated prompt object.
  - `400 Bad Request`: Validation errors.
  - `404 Not Found`: If prompt doesn't exist.

#### Example Response

```json
{
  "id": "uuid-string",
  "coaching_phase": "INTRODUCTION",
  "version": 1,
  "name": "Updated Welcome Message",
  "description": "Updated initial greeting for new users",
  "body": "Welcome to Dev Coach! I'm here to help you on your journey...",
  "required_context_keys": ["user_name", "coaching_phase", "user_goals"],
  "allowed_actions": [
    "TRANSITION_PHASE",
    "CREATE_IDENTITY",
    "UPDATE_WHO_YOU_ARE"
  ],
  "prompt_type": "COACH",
  "is_active": true,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-06-01T12:00:00Z"
}
```

---

### 5. Update Prompt (Partial Update)

- **URL:** `/prompts/{id}/`
- **Method:** `PATCH`
- **Description:** Partially update a prompt with only the provided fields.
- **Authentication:** Required
- **Request Body:**
  ```json
  {
    "name": "Updated Welcome Message",
    "description": "Updated initial greeting for new users"
  }
  ```
- **Response:**
  - `200 OK`: Updated prompt object.
  - `400 Bad Request`: Validation errors.
  - `404 Not Found`: If prompt doesn't exist.
  - `500 Internal Server Error`: Server errors.

#### Example Response

```json
{
  "success": false,
  "error": "Validation error",
  "detail": {
    "body": ["This field is required."]
  }
}
```

---

### 6. Delete Prompt

- **URL:** `/prompts/{id}/`
- **Method:** `DELETE`
- **Description:** Permanently delete a prompt.
- **Authentication:** Required
- **Response:**
  - `204 No Content`: Prompt deleted successfully.
  - `404 Not Found`: If prompt doesn't exist.

---

### 7. Get Latest Prompt

- **URL:** `/prompts/latest/`
- **Method:** `GET`
- **Description:** Get the most recent active prompt for a specific coaching phase.
- **Authentication:** Required
- **Query Parameters:**
  - `coaching_phase` (required): The coaching phase to get the latest prompt for
- **Response:**
  - `200 OK`: The most recent active prompt for the specified phase.
  - `400 Bad Request`: Missing or invalid coaching_phase parameter.
  - `404 Not Found`: No active prompt found for the specified phase.
  - `500 Internal Server Error`: Server error.

#### Example Request

```
GET /prompts/latest/?coaching_phase=introduction
```

#### Example Response (Success)

```json
{
  "id": "uuid-string",
  "coaching_phase": "introduction",
  "version": 3,
  "name": "Latest Welcome Message",
  "description": "Most recent greeting for new users",
  "body": "Welcome to Dev Coach! I'm here to help you on your journey...",
  "required_context_keys": ["user_name", "coaching_phase"],
  "allowed_actions": ["TRANSITION_PHASE", "CREATE_IDENTITY"],
  "prompt_type": "COACH",
  "is_active": true,
  "created_at": "2024-06-01T12:00:00Z",
  "updated_at": "2024-06-01T12:00:00Z"
}
```

#### Example Response (Missing Parameter)

```json
{
  "success": false,
  "error": "Missing required parameter",
  "detail": "coaching_phase query parameter is required"
}
```

#### Example Response (Invalid Coaching Phase)

```json
{
  "success": false,
  "error": "Invalid coaching phase",
  "detail": "Invalid coaching_phase: invalid_phase. Valid phases: ['system_context', 'introduction', 'get_to_know_you', 'identity_warm_up', 'identity_brainstorming', 'identity_refinement', 'i_am_statement', 'identity_visualization']"
}
```

#### Example Response (No Prompt Found)

```json
{
  "success": false,
  "error": "No prompt found",
  "detail": "No active prompt found for coaching phase: introduction"
}
```

#### Example Response (Server Error)

```json
{
  "success": false,
  "error": "Server error",
  "detail": "An error occurred while retrieving the latest prompt"
}
```

---

### 8. Soft Delete Prompt

- **URL:** `/prompts/{id}/soft_delete/`
- **Method:** `POST`
- **Description:** Soft delete a prompt by setting `is_active` to `False` instead of permanently deleting it.
- **Authentication:** Required
- **Response:**
  - `200 OK`: Updated prompt object with `is_active=False`.

#### Example Response

```json
{
  "id": "uuid-string",
  "coaching_phase": "INTRODUCTION",
  "version": 1,
  "name": "Welcome Message",
  "description": "Initial greeting for new users",
  "body": "Welcome to Dev Coach! I'm here to help you...",
  "required_context_keys": ["user_name", "coaching_phase"],
  "allowed_actions": ["TRANSITION_PHASE", "CREATE_IDENTITY"],
  "prompt_type": "COACH",
  "is_active": false,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-06-01T12:00:00Z"
}
```

---

## Field Reference

For detailed field information on the Prompt model, see:

- **[Prompt Fields](../../database/models/prompt)** - Prompt model fields and structure

---

## Notes

- The `list` endpoint only returns prompts with `is_active=True`.
- When creating a new prompt, the `version` field is automatically assigned as the next version number:
  - For prompts with `coaching_phase`: versions are unique per (`prompt_type`, `coaching_phase`)
  - For prompts without `coaching_phase` (e.g., `image_generation`, `sentinel`): versions are unique per `prompt_type`
- The combination of `prompt_type`, `coaching_phase`, and `version` must be unique.
- Soft delete is preferred over hard delete to maintain data integrity. The front end only uses the Soft Delete.
- All endpoints require authentication.
