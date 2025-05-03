# Prompts API Documentation

This document describes the REST API endpoints for managing Prompts.

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
    "id": "uuid-string",
    "owner": 1,
    "prompt_key": "example-key",
    "version": 1,
    "name": "Prompt Name",
    "description": "Prompt description.",
    "body": "Prompt body text.",
    "required_context_keys": ["key1", "key2"],
    "is_active": true,
    "created_at": "2024-06-01T12:00:00Z",
    "updated_at": "2024-06-01T12:00:00Z"
  }
]
```

---

### 2. Retrieve a Single Prompt

- **URL:** `/api/prompts/{id}/`
- **Method:** `GET`
- **Description:** Returns a single prompt by its ID.
- **Response:**
    - `200 OK`: Prompt object.
    - `404 Not Found`: If the prompt does not exist.

---

### 3. Create a New Prompt

- **URL:** `/api/prompts/`
- **Method:** `POST`
- **Description:** Creates a new prompt.
- **Body Parameters:**
    - All fields from the Prompt model (see PromptSerializer).
- **Response:**
    - `201 Created`: Created prompt object.
    - `400 Bad Request`: Validation errors.

#### Example Request Body
```json
{
  "owner": 1,
  "prompt_key": "example-key",
  "version": 1,
  "name": "Prompt Name",
  "description": "Prompt description.",
  "body": "Prompt body text.",
  "required_context_keys": ["key1", "key2"],
  "is_active": true
}
```

---

### 4. Update a Prompt (Full Update)

- **URL:** `/api/prompts/{id}/`
- **Method:** `PUT`
- **Description:** Updates all fields of a prompt.
- **Body Parameters:**
    - All fields from the Prompt model (see PromptSerializer).
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
- Authentication and permissions are not described here but should be enforced as appropriate.
- Update this document whenever the API changes. 