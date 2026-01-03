---
sidebar_position: 9
---

# Reference Image

The Reference Image model stores user-uploaded photos used as input for AI-powered identity image generation. Each user can have up to 5 reference images that are used by the Gemini image generation service to create personalized identity visualizations.

## Overview

Reference images serve as the source material for generating identity images. When a user wants to visualize themselves as a particular identity (e.g., "Creative Visionary"), the system uses these reference photos along with identity context to generate a personalized image using the Gemini AI service.

## Fields

- `id` (UUIDField): Primary key, auto-generated UUID
- `user` (ForeignKey): Link to [User](./users.md) model
- `name` (CharField): Optional label for this image (e.g., "Headshot 1"), max 255 characters
- `order` (PositiveSmallIntegerField): Display order slot (0-4), defaults to 0
- `image` (VersatileImageField): The uploaded image file, stored in S3 (inherited from ImageMixin)
- `image_ppoi` (PPOIField): Primary Point of Interest for smart cropping (inherited from ImageMixin)
- `created_at` (DateTimeField): Creation timestamp, auto-set
- `updated_at` (DateTimeField): Last update timestamp, auto-updated

## Configuration

- `ordering`: `["order", "-created_at"]`
- Constraint: Unique combination of `user` and `order` (one image per slot per user)

## Inheritance

Reference Image inherits from:
- `ImageMixin`: Provides VersatileImageField with automatic S3 storage and size variant generation
- `models.Model`: Django base model

## Methods

- `__str__()`: Returns "{user.email} - Reference Image {order + 1}"
- `create_image_sizes()`: Enables on-demand image size creation (inherited from ImageMixin)

## Relationships

- Many-to-One with [User](./users.md) (via `reference_images`)

## Constraints

- **Maximum 5 per user**: Enforced by order range (0-4) and unique constraint
- **Unique order per user**: Database-level constraint ensures no duplicate order slots

## Image Storage

Reference images use the `ImageMixin` which provides:
- **S3 Storage**: Images stored in AWS S3 via `django-storages`
- **UUID Paths**: File paths use UUID to prevent naming conflicts
- **Auto Resizing**: VersatileImageField generates multiple size variants:
  - Original (full size)
  - Thumbnail (100x100)
  - Medium (300x300)
  - Large (600x600)

## Admin Panel

Reference images are integrated into the Django Admin panel:

- **Inline Display**: Reference images appear inline when viewing/editing a User
- **Thumbnail Previews**: Image thumbnails are displayed for quick visual reference
- **Direct Management**: Standalone admin interface for managing reference images directly
- **Read-Only Fields**: `id`, `created_at`, `updated_at` are read-only
- **Image Upload**: Images can be uploaded directly through the admin panel

## Logging

All reference image operations include comprehensive logging:

- **Model Operations**: Logs when images are created, updated, or deleted
- **Image Processing**: Logs S3 upload operations and image size generation
- **Error Tracking**: All errors are logged with full context for debugging

Logs help identify:
- Slow S3 operations
- Image processing bottlenecks
- Database constraint violations
- Serialization issues

## Admin Panel

Reference images are integrated into the Django Admin panel:

- **Inline Display**: Reference images appear inline when viewing/editing a User
- **Thumbnail Previews**: Image thumbnails are displayed for quick visual reference
- **Direct Management**: Standalone admin interface for managing reference images directly
- **Read-Only Fields**: `id`, `created_at`, `updated_at` are read-only
- **Image Upload**: Images can be uploaded directly through the admin panel

## Logging

All reference image operations include comprehensive logging:

- **Model Operations**: Logs when images are created, updated, or deleted
- **Image Processing**: Logs S3 upload operations and image size generation
- **Error Tracking**: All errors are logged with full context for debugging

Logs help identify:
- Slow S3 operations
- Image processing bottlenecks
- Database constraint violations
- Serialization issues

## Usage Context

- Stores user's reference photos for AI image generation
- Used by the Image Generation service to create identity visualizations
- Admin users can manage reference images for test users
- Part of the admin-only Images tab workflow
- Referenced when generating identity images via the Gemini API
- Accessible through Django Admin panel with inline display
- Frontend components provide user-friendly management interface
- Accessible through Django Admin panel with inline display
- Frontend components provide user-friendly management interface

