# Identities

## Base URL

`/identities/`

---

## Endpoints

### 1. List Identities

- **URL:** `/identities/`
- **Method:** `GET`
- **Description:** List all identities for the authenticated user. By default, archived identities are excluded from the results.
- **Authentication:** Required
- **Query Parameters:**
  - `include_archived` (optional): Set to `true` to include archived identities in the results. Default: `false`
  - `archived_only` (optional): Set to `true` to return only archived identities. Default: `false`
- **Response:**
  - `200 OK`: Array of identity objects belonging to the authenticated user (excluding archived by default).
  - `500 Internal Server Error`: Server error.

#### Example Request

```
GET /identities/
GET /identities/?include_archived=true
GET /identities/?archived_only=true
```

#### Example Response

```json
[
  {
    "id": "uuid-string",
    "user": "user-uuid",
    "name": "Creative Visionary",
    "i_am_statement": "I am a bold creator, transforming ideas into reality.",
    "visualization": "I see myself confidently presenting innovative solutions...",
    "clothing": "linen button-down shirt",
    "mood": "proud and calm",
    "setting": "on a hill overlooking Hawaiian agricultural land",
    "state": "ACCEPTED",
    "notes": ["Note 1", "Note 2"],
    "category": "PASSIONS",
    "image": "https://discovita-dev-coach-staging.s3.amazonaws.com/media/identities/2024/06/01/image.png",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-06-01T12:00:00Z"
  },
  {
    "id": "uuid-string",
    "user": "user-uuid",
    "name": "Warrior",
    "i_am_statement": "I treat my body with strength, discipline, and respect.",
    "visualization": "I see myself in peak physical condition...",
    "clothing": null,
    "mood": null,
    "setting": null,
    "state": "ACCEPTED",
    "notes": [],
    "category": "PHYSICAL_HEALTH",
    "image": null,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-06-01T12:00:00Z"
  }
]
```

---

### 2. Retrieve Identity

- **URL:** `/identities/{id}/`
- **Method:** `GET`
- **Description:** Retrieve a single identity by ID. Only returns identities belonging to the authenticated user. Archived identities can be retrieved by ID even though they are excluded from list endpoints by default.
- **Authentication:** Required
- **Response:**
  - `200 OK`: Identity object (including archived identities if accessed by ID).
  - `404 Not Found`: If identity doesn't exist or doesn't belong to the user.
  - `500 Internal Server Error`: Server error.

#### Example Response

```json
{
  "id": "uuid-string",
  "user": "user-uuid",
  "name": "Creative Visionary",
  "i_am_statement": "I am a bold creator, transforming ideas into reality.",
  "visualization": "I see myself confidently presenting innovative solutions...",
  "clothing": "linen button-down shirt",
  "mood": "proud and calm",
  "setting": "on a hill overlooking Hawaiian agricultural land",
  "state": "ACCEPTED",
  "notes": ["Note 1", "Note 2"],
  "category": "PASSIONS",
  "image": "https://discovita-dev-coach-staging.s3.amazonaws.com/media/identities/2024/06/01/image.png",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-06-01T12:00:00Z"
}
```

---

### 3. Create Identity

- **URL:** `/identities/`
- **Method:** `POST`
- **Description:** Create a new identity for the authenticated user. The `user` field is automatically set to the authenticated user and cannot be specified in the request.
- **Authentication:** Required
- **Request Body:**
  ```json
  {
    "name": "Creative Visionary",
    "i_am_statement": "I am a bold creator, transforming ideas into reality.",
    "visualization": "I see myself confidently presenting innovative solutions...",
    "clothing": "linen button-down shirt",
    "mood": "proud and calm",
    "setting": "on a hill overlooking Hawaiian agricultural land",
    "state": "PROPOSED",
    "notes": ["Initial note about this identity"],
    "category": "PASSIONS"
  }
  ```
- **Response:**
  - `201 Created`: Created identity object.
  - `400 Bad Request`: Validation errors.
  - `500 Internal Server Error`: Server error.

#### Example Response

```json
{
  "id": "uuid-string",
  "user": "user-uuid",
  "name": "Creative Visionary",
  "i_am_statement": "I am a bold creator, transforming ideas into reality.",
  "visualization": "I see myself confidently presenting innovative solutions...",
  "clothing": "linen button-down shirt",
  "mood": "proud and calm",
  "setting": "on a hill overlooking Hawaiian agricultural land",
  "state": "PROPOSED",
  "notes": ["Initial note about this identity"],
  "category": "PASSIONS",
  "image": null,
  "created_at": "2024-06-01T12:00:00Z",
  "updated_at": "2024-06-01T12:00:00Z"
}
```

**Note:** The `user` field is read-only and automatically set to the authenticated user. The `id`, `created_at`, and `updated_at` fields are automatically generated.

---

### 4. Update Identity (Full Update)

- **URL:** `/identities/{id}/`
- **Method:** `PUT`
- **Description:** Update an identity with all fields (full update). Only identities belonging to the authenticated user can be updated.
- **Authentication:** Required
- **Request Body:**
  ```json
  {
    "name": "Updated Creative Visionary",
    "i_am_statement": "I am a bold creator, transforming ideas into reality with passion and purpose.",
    "visualization": "I see myself confidently presenting innovative solutions to large audiences...",
    "clothing": "formal conductor's attire",
    "mood": "passionate and focused",
    "setting": "grand concert hall",
    "state": "ACCEPTED",
    "notes": ["Updated note 1", "Updated note 2"],
    "category": "PASSIONS"
  }
  ```
- **Response:**
  - `200 OK`: Updated identity object.
  - `400 Bad Request`: Validation errors.
  - `404 Not Found`: If identity doesn't exist or doesn't belong to the user.
  - `500 Internal Server Error`: Server error.

#### Example Response

```json
{
  "id": "uuid-string",
  "user": "user-uuid",
  "name": "Updated Creative Visionary",
  "i_am_statement": "I am a bold creator, transforming ideas into reality with passion and purpose.",
  "visualization": "I see myself confidently presenting innovative solutions to large audiences...",
  "clothing": "formal conductor's attire",
  "mood": "passionate and focused",
  "setting": "grand concert hall",
  "state": "ACCEPTED",
  "notes": ["Updated note 1", "Updated note 2"],
  "category": "PASSIONS",
  "image": "https://discovita-dev-coach-staging.s3.amazonaws.com/media/identities/2024/06/01/image.png",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-06-01T13:00:00Z"
}
```

---

### 5. Update Identity (Partial Update)

- **URL:** `/identities/{id}/`
- **Method:** `PATCH`
- **Description:** Partially update an identity with only the provided fields. Only identities belonging to the authenticated user can be updated.
- **Authentication:** Required
- **Request Body:**
  ```json
  {
    "name": "Updated Creative Visionary",
    "clothing": "linen button-down shirt",
    "state": "ACCEPTED"
  }
  ```
- **Response:**
  - `200 OK`: Updated identity object.
  - `400 Bad Request`: Validation errors.
  - `404 Not Found`: If identity doesn't exist or doesn't belong to the user.
  - `500 Internal Server Error`: Server error.

#### Example Response

```json
{
  "id": "uuid-string",
  "user": "user-uuid",
  "name": "Updated Creative Visionary",
  "i_am_statement": "I am a bold creator, transforming ideas into reality.",
  "visualization": "I see myself confidently presenting innovative solutions...",
  "clothing": "linen button-down shirt",
  "mood": null,
  "setting": null,
  "state": "ACCEPTED",
  "notes": ["Note 1", "Note 2"],
  "category": "PASSIONS",
  "image": null,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-06-01T13:00:00Z"
}
```

---

### 6. Delete Identity

- **URL:** `/identities/{id}/`
- **Method:** `DELETE`
- **Description:** Permanently delete an identity. If the identity has an associated image, the image file will also be deleted. Only identities belonging to the authenticated user can be deleted.
- **Authentication:** Required
- **Response:**
  - `204 No Content`: Identity deleted successfully.
  - `404 Not Found`: If identity doesn't exist or doesn't belong to the user.
  - `500 Internal Server Error`: Server error.

**Note:** This operation is permanent and cannot be undone. The associated image file (if any) will also be deleted from storage.

---

### 7. Upload Identity Image

- **URL:** `/identities/{id}/upload-image/`
- **Method:** `PATCH` or `PUT`
- **Description:** Upload or update the image for an identity. If an image already exists, it will be replaced. Only identities belonging to the authenticated user can be updated.
- **Authentication:** Required
- **Content-Type:** `multipart/form-data`
- **Request Body:**
  - Form data with field name `image` containing the image file
- **Response:**
  - `200 OK`: Updated identity object with image URL.
  - `400 Bad Request`: No image file provided.
  - `404 Not Found`: If identity doesn't exist or doesn't belong to the user.
  - `403 Forbidden`: Permission denied.
  - `500 Internal Server Error`: Server error.

#### Example Request

```
PATCH /identities/{id}/upload-image/
Content-Type: multipart/form-data

image: [binary file data]
```

#### Example Response

```json
{
  "id": "uuid-string",
  "user": "user-uuid",
  "name": "Creative Visionary",
  "i_am_statement": "I am a bold creator, transforming ideas into reality.",
  "visualization": "I see myself confidently presenting innovative solutions...",
  "clothing": "linen button-down shirt",
  "mood": "proud and calm",
  "setting": "on a hill overlooking Hawaiian agricultural land",
  "state": "ACCEPTED",
  "notes": ["Note 1", "Note 2"],
  "category": "PASSIONS",
  "image": "https://discovita-dev-coach-staging.s3.amazonaws.com/media/identities/2024/06/01/new-image.png",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-06-01T13:00:00Z"
}
```

**Note:** 
- The image is automatically stored in S3 (production/staging) or local media directory (development).
- Image path format: `media/identities/YYYY/MM/DD/filename.ext`
- If an existing image is present, it will be deleted before uploading the new one.
- Supported image formats depend on Django's ImageField configuration.

---

### 8. Delete Identity Image

- **URL:** `/identities/{id}/delete-image/`
- **Method:** `DELETE`
- **Description:** Delete the image associated with an identity. The image file will be removed from storage. Only identities belonging to the authenticated user can be updated.
- **Authentication:** Required
- **Response:**
  - `200 OK`: Updated identity object without image (image field will be `null`).
  - `404 Not Found`: If identity doesn't exist, doesn't belong to the user, or has no image to delete.
  - `403 Forbidden`: Permission denied.
  - `500 Internal Server Error`: Server error.

#### Example Response

```json
{
  "id": "uuid-string",
  "user": "user-uuid",
  "name": "Creative Visionary",
  "i_am_statement": "I am a bold creator, transforming ideas into reality.",
  "visualization": "I see myself confidently presenting innovative solutions...",
  "clothing": null,
  "mood": null,
  "setting": null,
  "state": "ACCEPTED",
  "notes": ["Note 1", "Note 2"],
  "category": "PASSIONS",
  "image": null,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-06-01T13:00:00Z"
}
```

---

### 9. Download I Am Statements PDF

- **URL:** `/identities/download-i-am-statements-pdf/`
- **Method:** `GET`
- **Description:** Download a PDF document containing all of the authenticated user's completed I Am statements. The PDF includes identity names, categories, and I Am statements in a two-column layout.
- **Authentication:** Required
- **Response:**
  - `200 OK`: PDF file download.
  - `400 Bad Request`: No completed identities found for the user.
  - `500 Internal Server Error`: Server error.

#### Example Request

```
GET /identities/download-i-am-statements-pdf/
```

#### Response Headers

```
Content-Type: application/pdf
Content-Disposition: attachment; filename="i-am-statements-{user-name}.pdf"
```

**Note:** 
- Only identities with `state = I_AM_COMPLETE` are included in the PDF.
- Archived identities are excluded.
- If the user has no completed identities, a 400 error is returned.

---

### 10. Download I Am Statements PDF for User (Admin Only)

- **URL:** `/admin/identities/download-i-am-statements-pdf-for-user/`
- **Method:** `GET`
- **Description:** Admin endpoint to download a PDF of I Am statements for any user by ID.
- **Authentication:** Required (Admin only)
- **Query Parameters:**
  - `user_id` (required): The ID of the user to generate the PDF for.
- **Response:**
  - `200 OK`: PDF file download.
  - `400 Bad Request`: Missing `user_id` parameter or no completed identities found.
  - `404 Not Found`: User not found.
  - `500 Internal Server Error`: Server error.

#### Example Request

```
GET /admin/identities/download-i-am-statements-pdf-for-user/?user_id=abc123
```

#### Response Headers

```
Content-Type: application/pdf
Content-Disposition: attachment; filename="i-am-statements-{user-name}.pdf"
```

**Note:** This endpoint is only accessible to admin users.

---

## Field Reference

### Identity Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID (string) | Auto-generated | Unique identifier for the identity |
| `user` | UUID (string) | Read-only | User ID this identity belongs to (automatically set to authenticated user) |
| `name` | String (max 255) | Optional | Concise label for the identity (e.g., 'Creative Visionary') |
| `i_am_statement` | Text | Optional | An 'I am' statement with a brief description |
| `visualization` | Text | Optional | A vivid mental image (added in the visualization stage) |
| `clothing` | Text | Optional | What the person is wearing in this identity visualization (e.g., 'linen button-down shirt') |
| `mood` | Text | Optional | Emotional state/feeling in this identity visualization (e.g., 'proud and calm') |
| `setting` | Text | Optional | Environment/location for this identity visualization (e.g., 'on a hill overlooking the ocean') |
| `state` | String | Optional | Current state of the identity. See [Identity State Choices](#identity-state-choices) |
| `notes` | Array of Strings | Optional | List of notes about the identity |
| `category` | String | Required | Category this identity belongs to. See [Identity Category Choices](#identity-category-choices) |
| `image` | String (URL) or null | Optional | URL to the image associated with this identity. Stored in S3 (production/staging) or local media (development) |
| `created_at` | DateTime (ISO 8601) | Auto-generated | Timestamp when the identity was created |
| `updated_at` | DateTime (ISO 8601) | Auto-updated | Timestamp when the identity was last updated |

### Identity State Choices

The `state` field accepts the following values:

- `PROPOSED`: Identity has been proposed but not yet accepted
- `ACCEPTED`: Identity has been accepted by the user
- `REFINEMENT_COMPLETE`: Identity refinement process is complete
- `COMMITMENT_COMPLETE`: User has committed to the identity and wants to advance to the I Am Statement Phase
- `I_AM_COMPLETE`: User has created an I Am statement for the identity
- `VISUALIZATION_COMPLETE`: User has created a visualization for the identity
- `ARCHIVED`: Identity has been archived and is excluded from active coaching workflows by default

### Identity Category Choices

The `category` field accepts the following values (see `enums/identity_category.py` for complete list):

- `PASSIONS`: Passion-based identities
- `VALUES`: Value-based identities
- `STRENGTHS`: Strength-based identities
- `PHYSICAL_HEALTH`: Physical health-related identities
- `MENTAL_HEALTH`: Mental health-related identities
- `RELATIONSHIPS`: Relationship-based identities
- `CAREER`: Career-related identities
- `FINANCIAL`: Financial-related identities
- `SPIRITUAL`: Spiritual identities
- `CREATIVE`: Creative identities

---

## Identity Image Chat Endpoints

These endpoints enable multi-turn image generation using Gemini's chat functionality. Users can start a new image generation session and then iteratively refine the generated image through conversation.

### 11. Start Image Chat

- **URL:** `/identity-image-chat/start/`
- **Method:** `POST`
- **Description:** Start a new image generation chat session for an identity. Creates a new Gemini chat, generates the initial image using the user's reference images and identity context, and stores the chat history for future edits. If a chat session already exists for the user, it will be replaced.
- **Authentication:** Required
- **Request Body:**
  ```json
  {
    "identity_id": "uuid-string",
    "additional_prompt": "optional extra instructions for the image generation"
  }
  ```
- **Response:**
  - `200 OK`: Generated image and identity information.
  - `400 Bad Request`: No reference images found for user, or validation errors.
  - `404 Not Found`: Identity not found.
  - `500 Internal Server Error`: Image generation failed.

#### Example Request

```
POST /identity-image-chat/start/
Content-Type: application/json

{
  "identity_id": "abc123-uuid",
  "additional_prompt": "Make the lighting dramatic"
}
```

#### Example Response

```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "identity_id": "abc123-uuid",
  "identity_name": "The Artist"
}
```

**Note:**
- Requires at least one reference image uploaded for the user.
- The chat session is stored and can be continued with the Continue Image Chat endpoint.
- Only one chat session exists per user; starting a new chat replaces any existing session.

---

### 12. Continue Image Chat

- **URL:** `/identity-image-chat/continue/`
- **Method:** `POST`
- **Description:** Continue an existing image chat session with an edit request. Loads the user's existing chat history, sends the edit prompt to Gemini, and returns the newly generated image.
- **Authentication:** Required
- **Request Body:**
  ```json
  {
    "edit_prompt": "make the lighting warmer"
  }
  ```
- **Response:**
  - `200 OK`: Generated image and identity information.
  - `400 Bad Request`: No active chat session, empty edit prompt, or validation errors.
  - `500 Internal Server Error`: Image generation failed.

#### Example Request

```
POST /identity-image-chat/continue/
Content-Type: application/json

{
  "edit_prompt": "Add more vibrant colors to the background"
}
```

#### Example Response

```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "identity_id": "abc123-uuid",
  "identity_name": "The Artist"
}
```

**Note:**
- Requires an active chat session (must call Start Image Chat first).
- The chat history is preserved, allowing Gemini to understand the context of previous messages and images.
- Multiple edit requests can be made to iteratively refine the image.

---

### 13. Start Image Chat (Admin)

- **URL:** `/admin/identity-image-chat/start/`
- **Method:** `POST`
- **Description:** Admin endpoint to start a new image generation chat session for any user by ID.
- **Authentication:** Required (Admin only)
- **Request Body:**
  ```json
  {
    "identity_id": "uuid-string",
    "user_id": "uuid-string",
    "additional_prompt": "optional extra instructions"
  }
  ```
- **Response:**
  - `200 OK`: Generated image and identity information.
  - `400 Bad Request`: No reference images found for user, or validation errors.
  - `404 Not Found`: Identity or user not found.
  - `500 Internal Server Error`: Image generation failed.

#### Example Request

```
POST /admin/identity-image-chat/start/
Content-Type: application/json

{
  "identity_id": "abc123-uuid",
  "user_id": "user456-uuid",
  "additional_prompt": "Make it more vibrant"
}
```

#### Example Response

```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "identity_id": "abc123-uuid",
  "identity_name": "The Artist"
}
```

**Note:** This endpoint is only accessible to admin users.

---

### 14. Continue Image Chat (Admin)

- **URL:** `/admin/identity-image-chat/continue/`
- **Method:** `POST`
- **Description:** Admin endpoint to continue an existing image chat session for any user by ID.
- **Authentication:** Required (Admin only)
- **Request Body:**
  ```json
  {
    "user_id": "uuid-string",
    "edit_prompt": "make the lighting warmer"
  }
  ```
- **Response:**
  - `200 OK`: Generated image and identity information.
  - `400 Bad Request`: No active chat session, empty edit prompt, or validation errors.
  - `404 Not Found`: User not found.
  - `500 Internal Server Error`: Image generation failed.

#### Example Request

```
POST /admin/identity-image-chat/continue/
Content-Type: application/json

{
  "user_id": "user456-uuid",
  "edit_prompt": "Remove the hat"
}
```

#### Example Response

```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "identity_id": "abc123-uuid",
  "identity_name": "The Artist"
}
```

**Note:** This endpoint is only accessible to admin users.

---

## Notes

- All endpoints require authentication. See the authentication documentation for details.
- All operations are scoped to the authenticated user's identities only. Users cannot access or modify identities belonging to other users.
- The `user` field is read-only and automatically set to the authenticated user when creating identities.
- **Archived Identities**: Archived identities are excluded from list endpoints by default but can be accessed:
  - Via query parameters: `?include_archived=true` to include them, or `?archived_only=true` to see only archived identities
  - By direct ID retrieval: Archived identities can be retrieved using the `GET /identities/{id}/` endpoint
  - Archived identities are excluded from all active coaching workflows (context functions, action handlers, etc.)
- Image uploads use `multipart/form-data` content type. The image field name in the form data must be `image`.
- Images are automatically stored in:
  - **Production/Staging**: S3 bucket (`discovita-dev-coach-production` or `discovita-dev-coach-staging`)
  - **Development**: Local media directory (`.media/identities/YYYY/MM/DD/`)
- Image URLs are automatically generated and returned in responses. In production/staging, these will be S3 URLs. In development, these will be local URLs served by Django.
- When deleting an identity, any associated image file is also deleted from storage.
- When uploading a new image, any existing image is automatically deleted before the new one is saved.
- Field values for enums must match the choices defined in their respective enum files:
  - `state`: see `enums/identity_state.py`
  - `category`: see `enums/identity_category.py`
- The `notes` field is an array of strings. When updating, you can provide a new array to replace all notes, or use partial update to modify specific fields.

### Image Chat Notes

- **Multi-turn Image Generation**: The identity image chat endpoints use Gemini's multi-turn conversation feature to enable iterative image refinement.
- **Chat Session Persistence**: Chat history is stored in the `IdentityImageChat` model. Only one session exists per user; starting a new chat replaces any existing session.
- **Reference Images Required**: The user must have at least one reference image uploaded before starting an image chat.
- **Base64 Response**: Generated images are returned as base64-encoded PNG strings in the `image_base64` field.
- **Context Preservation**: The chat history includes all previous messages and generated images, allowing Gemini to understand the full context when processing edit requests.
- **Typical Workflow**:
  1. Upload reference images (see Reference Images API)
  2. Call `/identity-image-chat/start/` to generate the initial image
  3. Call `/identity-image-chat/continue/` with edit prompts to refine the image
  4. Repeat step 3 as needed until satisfied
  5. Save the final image to the identity using `/identities/{id}/upload-image/`

- Update this document whenever the API changes.

