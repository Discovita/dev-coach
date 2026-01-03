# Reference Images

## Base URL

`/reference-images/`

---

## Overview

Reference images are user-uploaded photos used as input for AI-powered identity image generation. Each user can have up to 5 reference images stored in S3. These images are used by the Gemini image generation service to create personalized identity visualizations.

---

## Endpoints

### 1. List Reference Images

- **URL:** `/reference-images/`
- **Method:** `GET`
- **Description:** List all reference images for the authenticated user. Admin users can list images for other users by providing a `user_id` query parameter.
- **Authentication:** Required
- **Query Parameters:**
  - `user_id` (optional, admin only): UUID of the user whose reference images to retrieve. Non-admin users will have this parameter ignored.
- **Response:**
  - `200 OK`: Array of reference image objects.
  - `401 Unauthorized`: Authentication required.
  - `500 Internal Server Error`: Server error.

#### Example Request

```
GET /reference-images/
GET /reference-images/?user_id=abc123-def456  (admin only)
```

#### Example Response

```json
[
  {
    "id": "uuid-string",
    "user": "user-uuid",
    "name": "Headshot 1",
    "order": 0,
    "image": {
      "original": "https://bucket.s3.amazonaws.com/media/uuid/image.jpg",
      "thumbnail": "https://bucket.s3.amazonaws.com/media/uuid/__sized__/image-thumbnail-100x100.jpg",
      "medium": "https://bucket.s3.amazonaws.com/media/uuid/__sized__/image-thumbnail-300x300.jpg",
      "large": "https://bucket.s3.amazonaws.com/media/uuid/__sized__/image-thumbnail-600x600.jpg"
    },
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-06-01T12:00:00Z"
  },
  {
    "id": "uuid-string-2",
    "user": "user-uuid",
    "name": "Profile Photo",
    "order": 1,
    "image": null,
    "created_at": "2024-01-02T12:00:00Z",
    "updated_at": "2024-01-02T12:00:00Z"
  }
]
```

---

### 2. Retrieve Reference Image

- **URL:** `/reference-images/{id}/`
- **Method:** `GET`
- **Description:** Retrieve a single reference image by ID. Only returns reference images belonging to the authenticated user (or any user's images for admins with `user_id` filter active).
- **Authentication:** Required
- **Response:**
  - `200 OK`: Reference image object.
  - `404 Not Found`: If reference image doesn't exist or doesn't belong to the user.
  - `500 Internal Server Error`: Server error.

#### Example Response

```json
{
  "id": "uuid-string",
  "user": "user-uuid",
  "name": "Headshot 1",
  "order": 0,
  "image": {
    "original": "https://bucket.s3.amazonaws.com/media/uuid/image.jpg",
    "thumbnail": "https://bucket.s3.amazonaws.com/media/uuid/__sized__/image-thumbnail-100x100.jpg",
    "medium": "https://bucket.s3.amazonaws.com/media/uuid/__sized__/image-thumbnail-300x300.jpg",
    "large": "https://bucket.s3.amazonaws.com/media/uuid/__sized__/image-thumbnail-600x600.jpg"
  },
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-06-01T12:00:00Z"
}
```

---

### 3. Create Reference Image

- **URL:** `/reference-images/`
- **Method:** `POST`
- **Description:** Create a new reference image slot for the authenticated user. Admin users can create for other users by providing `user_id` in the request body. Each user can have a maximum of 5 reference images.
- **Authentication:** Required
- **Content-Type:** `application/json` or `multipart/form-data` (if uploading image immediately)
- **Request Body:**
  ```json
  {
    "name": "Headshot 1",
    "order": 0,
    "user_id": "target-user-uuid"
  }
  ```
  
  | Field | Type | Required | Description |
  |-------|------|----------|-------------|
  | `name` | string | Optional | Label for this reference image |
  | `order` | integer (0-4) | Optional | Display order slot. If not provided, uses next available slot. |
  | `user_id` | UUID | Optional (admin only) | Target user ID. Non-admins will have this ignored. |
  | `image` | file | Optional | Image file (if using multipart/form-data) |

- **Response:**
  - `201 Created`: Created reference image object.
  - `400 Bad Request`: Validation error (max images reached, order already in use, order out of range).
  - `404 Not Found`: User not found (admin creating for other user).
  - `500 Internal Server Error`: Server error.

#### Example Response

```json
{
  "id": "uuid-string",
  "user": "user-uuid",
  "name": "Headshot 1",
  "order": 0,
  "image": null,
  "created_at": "2024-06-01T12:00:00Z",
  "updated_at": "2024-06-01T12:00:00Z"
}
```

#### Error Responses

**Maximum images reached (400):**
```json
{
  "detail": "Maximum 5 reference images allowed"
}
```

**Order already in use (400):**
```json
{
  "detail": "Order 2 is already in use"
}
```

**Order out of range (400):**
```json
{
  "detail": "Order must be between 0 and 4"
}
```

---

### 4. Update Reference Image (Partial Update)

- **URL:** `/reference-images/{id}/`
- **Method:** `PATCH`
- **Description:** Partially update a reference image's metadata (name, order). Only reference images belonging to the authenticated user can be updated.
- **Authentication:** Required
- **Request Body:**
  ```json
  {
    "name": "Updated Name"
  }
  ```
- **Response:**
  - `200 OK`: Updated reference image object.
  - `400 Bad Request`: Validation errors.
  - `404 Not Found`: If reference image doesn't exist or doesn't belong to the user.
  - `500 Internal Server Error`: Server error.

---

### 5. Delete Reference Image

- **URL:** `/reference-images/{id}/`
- **Method:** `DELETE`
- **Description:** Permanently delete a reference image and its associated image file from S3. Only reference images belonging to the authenticated user can be deleted.
- **Authentication:** Required
- **Response:**
  - `204 No Content`: Reference image deleted successfully.
  - `404 Not Found`: If reference image doesn't exist or doesn't belong to the user.
  - `500 Internal Server Error`: Server error.

**Note:** This operation is permanent and cannot be undone. The associated image file (if any) will also be deleted from S3 storage.

---

### 6. Upload Reference Image File

- **URL:** `/reference-images/{id}/upload-image/`
- **Method:** `POST`
- **Description:** Upload or replace the image file for a reference image slot. If an image already exists, it will be deleted and replaced.
- **Authentication:** Required
- **Content-Type:** `multipart/form-data`
- **Request Body:**
  - Form data with field name `image` containing the image file
- **Response:**
  - `200 OK`: Updated reference image object with image URLs.
  - `400 Bad Request`: No image file provided.
  - `404 Not Found`: If reference image doesn't exist or doesn't belong to the user.
  - `500 Internal Server Error`: Server error.

#### Example Request

```
POST /reference-images/{id}/upload-image/
Content-Type: multipart/form-data

image: [binary file data]
```

#### Example Response

```json
{
  "id": "uuid-string",
  "user": "user-uuid",
  "name": "Headshot 1",
  "order": 0,
  "image": {
    "original": "https://bucket.s3.amazonaws.com/media/uuid/new-image.jpg",
    "thumbnail": "https://bucket.s3.amazonaws.com/media/uuid/__sized__/new-image-thumbnail-100x100.jpg",
    "medium": "https://bucket.s3.amazonaws.com/media/uuid/__sized__/new-image-thumbnail-300x300.jpg",
    "large": "https://bucket.s3.amazonaws.com/media/uuid/__sized__/new-image-thumbnail-600x600.jpg"
  },
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-06-01T13:00:00Z"
}
```

#### Error Response

**No image file provided (400):**
```json
{
  "detail": "No image file provided"
}
```

---

## Field Reference

### Reference Image Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID (string) | Auto-generated | Unique identifier for the reference image |
| `user` | UUID (string) | Read-only | User ID this reference image belongs to |
| `name` | String (max 255) | Optional | Label for this reference image (e.g., "Headshot 1") |
| `order` | Integer (0-4) | Auto-assigned | Display order slot. Unique per user. |
| `image` | Object or null | Optional | Image URLs object with size variants (see below) |
| `created_at` | DateTime (ISO 8601) | Auto-generated | Timestamp when the reference image was created |
| `updated_at` | DateTime (ISO 8601) | Auto-updated | Timestamp when the reference image was last updated |

### Image Object Fields

When an image is uploaded, the `image` field returns an object with multiple size variants:

| Field | Type | Description |
|-------|------|-------------|
| `original` | String (URL) | Full-size original image |
| `thumbnail` | String (URL) | 100x100 pixel thumbnail |
| `medium` | String (URL) | 300x300 pixel medium size |
| `large` | String (URL) | 600x600 pixel large size |

If no image has been uploaded, the `image` field will be `null`.

---

## Constraints

- **Maximum 5 images per user**: Each user can have at most 5 reference images (order slots 0-4).
- **Unique order per user**: The combination of `user` and `order` must be unique. Attempting to create an image at an already-occupied order slot will fail.
- **Order range**: The `order` field must be between 0 and 4 (inclusive).

---

## Logging and Debugging

All reference image operations include comprehensive logging to help debug issues:

- **ViewSet Operations**: Logs queryset retrieval, serialization steps, and CRUD operations
- **Function Operations**: Logs image creation, upload, and deletion steps
- **Serialization**: Logs image URL generation for each size variant (original, thumbnail, medium, large)
- **Error Handling**: All errors are logged with full stack traces

Logs are available in the Django application logs and can help identify:
- Slow S3 operations (image URL generation)
- Serialization bottlenecks
- Database query issues
- Image processing problems

## Admin Panel Integration

Reference images can be managed through the Django Admin panel:

- **Inline Admin**: When viewing/editing a User in the admin panel, reference images are displayed inline with thumbnail previews
- **Standalone Admin**: Direct management of reference images is available through the ReferenceImage admin interface
- **Image Previews**: Thumbnail previews are shown for all images in the admin panel
- **Maximum Limit**: The admin enforces the 5-image limit per user

To access:
1. Navigate to Django Admin (`/admin/`)
2. Click on "Users" to view all users
3. Click on a specific user to see their reference images inline
4. Or navigate to "Reference Images" for direct management

## Frontend Components

The frontend includes dedicated components for managing reference images:

- **ReferenceImageManager**: Main component that displays all 5 slots in a responsive grid
- **ReferenceImageSlot**: Individual slot component with upload/replace/delete functionality
- **Integration**: Integrated into the admin-only Images page (`/images`)

Features:
- Visual grid layout (responsive: 1-5 columns based on screen size)
- Upload button for empty slots
- Replace and Delete buttons on hover for filled slots
- Loading states during operations
- Toast notifications for success/error feedback

## Notes

- All endpoints require authentication. See the authentication documentation for details.
- All operations are scoped to the authenticated user's reference images only, unless the user is an admin using the `user_id` parameter.
- The `user` field is read-only and automatically set to the authenticated user (or target user for admin operations).
- Images are stored in S3 using UUID-based paths to prevent naming conflicts.
- The `VersatileImageField` automatically generates multiple size variants when an image is uploaded.
- When uploading a new image, any existing image is automatically deleted before the new one is saved.
- Supported image formats depend on Django's ImageField and Pillow configuration.
- All operations include comprehensive logging for debugging purposes.
- Update this document whenever the API changes.

