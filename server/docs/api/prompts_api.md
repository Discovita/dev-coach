# Prompts API Documentation

## Base URL

`/api/prompts/`

---

## Endpoints

### 1. List All Prompts

- **URL:** `/api/prompts/`
- **Method:** `GET`
- **Description:** Returns a list of all prompts.
- **Response:**
  - `200 OK`: List of prompt objects.

#### Example Response

```json
[
  {
    "id": "uuid-string", // Unique identifier for this prompt
    "coach_state": "STATE_NAME", // The state of the coach (see enums/coaching_state.py)
    "version": 1, // Version number of the prompt
    "name": "Prompt Name", // Optional name
    "description": "Prompt description.", // Optional description
    "body": "Prompt body text.", // The main prompt text
    "required_context_keys": ["key1", "key2"], // List of required context keys (see enums/context_keys.py)
    "allowed_actions": ["ACTION_TYPE_1", "ACTION_TYPE_2"], // List of allowed action types (see enums/action_type.py)
    "is_active": true, // Whether the prompt is active
    "created_at": "2024-06-01T12:00:00Z", // Creation timestamp
    "updated_at": "2024-06-01T12:00:00Z" // Last update timestamp
  }
]
```

---

### 2. Retrieve a Single Prompt

- **URL:** `/api/prompts/{id}/`
- **Method:** `GET`
- **Description:** Returns a single prompt by its ID.
- **Response:**
  - `200 OK`: Prompt object (see above for fields).
  - `404 Not Found`: If the prompt does not exist.

---

### 3. Create a New Prompt

- **URL:** `/api/prompts/`
- **Method:** `POST`
- **Description:** Creates a new prompt.
- **Body Parameters:**
  - All fields from the Prompt model (see field reference above).
  - Fields marked as auto-generated (id, created_at, updated_at) are not required in the request.
- **Response:**
  - `201 Created`: Created prompt object.
  - `400 Bad Request`: Validation errors.

#### Example Request Body

```json
{
  "coach_state": "STATE_NAME", // Required, see enums/coaching_state.py
  "version": 1, // Required
  "name": "Prompt Name", // Optional
  "description": "Prompt description.", // Optional
  "body": "Prompt body text.", // Required
  "required_context_keys": ["key1", "key2"], // Required, see enums/context_keys.py
  "allowed_actions": ["ACTION_TYPE_1", "ACTION_TYPE_2"], // Optional, see enums/action_type.py
  "is_active": true // Optional, defaults to true
}
```

---

### 4. Update a Prompt (Full Update)

- **URL:** `/api/prompts/{id}/`
- **Method:** `PUT`
- **Description:** Updates all fields of a prompt.
- **Body Parameters:**
  - All fields from the Prompt model (see field reference above).
- **Response:**
  - `200 OK`: Updated prompt object.
  - `400 Bad Request`: Validation errors.
  - `404 Not Found`: If the prompt does not exist.

---

### 5. Partial Update a Prompt

- **URL:** `/api/prompts/{id}/`
- **Method:** `PATCH`
- **Description:** Updates one or more fields of a prompt.
- **Body Parameters:**
  - Any subset of fields from the Prompt model.
- **Response:**
  - `200 OK`: Updated prompt object.
  - `400 Bad Request`: Validation errors.
  - `404 Not Found`: If the prompt does not exist.

---

### 6. Delete a Prompt

- **URL:** `/api/prompts/{id}/`
- **Method:** `DELETE`
- **Description:** Deletes a prompt by its ID.
- **Response:**
  - `204 No Content`: Prompt deleted.
  - `404 Not Found`: If the prompt does not exist.

---

## Notes

- All endpoints return all fields of the Prompt model. See the PromptSerializer in `server/apps/prompts/serializers.py` for details.
- Field values for `coach_state`, `required_context_keys`, and `allowed_actions` must match the choices defined in their respective enums:
  - `coach_state`: see `enums/coaching_state.py`
  - `required_context_keys`: see `enums/context_keys.py`
  - `allowed_actions`: see `enums/action_type.py`
- Authentication and permissions are not described here but should be enforced as appropriate.
- Update this document whenever the API changes.
