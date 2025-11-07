# Identities

## Base URL

`/identities/`

---

## Endpoints

### 1. List Identities

- **URL:** `/identities/`
- **Method:** `GET`
- **Description:** List all identities for the authenticated user.
- **Authentication:** Required
- **Response:**
  - `200 OK`: Array of identity objects belonging to the authenticated user.
  - `500 Internal Server Error`: Server error.

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
- **Description:** Retrieve a single identity by ID. Only returns identities belonging to the authenticated user.
- **Authentication:** Required
- **Response:**
  - `200 OK`: Identity object.
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
  "state": "ACCEPTED",
  "notes": ["Note 1", "Note 2"],
  "category": "PASSIONS",
  "image": null,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-06-01T13:00:00Z"
}
```

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

## Notes

- All endpoints require authentication. See the authentication documentation for details.
- All operations are scoped to the authenticated user's identities only. Users cannot access or modify identities belonging to other users.
- The `user` field is read-only and automatically set to the authenticated user when creating identities.
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
- Update this document whenever the API changes.

