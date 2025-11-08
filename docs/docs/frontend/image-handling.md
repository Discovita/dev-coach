---
sidebar_position: 2
---

# Image Handling Guide

This guide explains how images are stored, processed, and used in both the backend and frontend of the Dev Coach application.

## Overview

The image system uses:
- **AWS S3** for cloud storage
- **django-versatileimagefield** for automatic image processing
- **UUID-based paths** for unique file storage
- **On-demand resizing** for multiple image sizes

## Backend Implementation

### Image Storage

Images are stored in S3 using UUID-based paths:
- Format: `media/{uuid}/{filename}`
- Example: `media/a361cc7b-100c-4510-8356-d8e731070d74/Casey-Schmid.jpg`

### Image Sizes

The backend automatically generates four image sizes:

| Size | Dimensions | Aspect Ratio | Use Case |
|------|------------|--------------|----------|
| **original** | Full size | Original | Downloads, lightboxes |
| **thumbnail** | 100x100 | Square (1:1) | Avatars, small cards |
| **medium** | 300x169 | 16:9 | Cards, lists |
| **large** | 600x338 | 16:9 | Hero sections, detail pages |

### API Response Format

When fetching identities from the API, the `image` field returns an object with all sizes:

```json
{
  "id": "123",
  "name": "Maker",
  "image": {
    "original": "https://discovita-dev-coach-staging.s3.amazonaws.com/media/uuid/image.jpg",
    "thumbnail": "https://discovita-dev-coach-staging.s3.amazonaws.com/media/uuid/__sized__/image-thumbnail-100x100-70.jpg",
    "medium": "https://discovita-dev-coach-staging.s3.amazonaws.com/media/uuid/__sized__/image-thumbnail-300x169-70.jpg",
    "large": "https://discovita-dev-coach-staging.s3.amazonaws.com/media/uuid/__sized__/image-thumbnail-600x338-70.jpg"
  }
}
```

### On-Demand Processing

Images are resized **on-demand** when first accessed:
1. First API call that includes the image triggers size generation
2. Resized images are stored in S3 under `__sized__` directory
3. Subsequent requests use the cached versions

This means:
- First access may be slower (generation happens)
- After generation, all sizes are cached in S3
- URLs are permanent once generated

## Frontend Implementation

### Type Definitions

The frontend uses TypeScript types that match the backend response:

```typescript
// client/src/types/imageSizes.ts
export interface ImageSizes {
  /** Full-size original image URL */
  original: string;
  /** 100x100 square thumbnail URL */
  thumbnail: string;
  /** 300x169 medium size URL (16:9 aspect ratio) */
  medium: string;
  /** 600x338 large size URL (16:9 aspect ratio) */
  large: string;
}

// client/src/types/identity.ts
export interface Identity {
  id?: string;
  name: string;
  // ... other fields
  image?: ImageSizes | null;
}
```

### Using Images in Components

#### Basic Usage

```typescript
import { Identity } from "@/types/identity";

function IdentityCard({ identity }: { identity: Identity }) {
  if (!identity.image) {
    return <div>No image available</div>;
  }

  return (
    <div>
      {/* Use medium for card view */}
      <img 
        src={identity.image.medium}
        alt={identity.name}
        className="w-full h-auto"
      />
    </div>
  );
}
```

#### Responsive Images with srcSet

```typescript
function IdentityCard({ identity }: { identity: Identity }) {
  if (!identity.image) return null;

  return (
    <img 
      src={identity.image.medium}
      srcSet={`
        ${identity.image.thumbnail} 100w,
        ${identity.image.medium} 300w,
        ${identity.image.large} 600w
      `}
      sizes="(max-width: 600px) 300px, 600px"
      alt={identity.name}
      loading="lazy"
    />
  );
}
```

#### Different Sizes for Different Contexts

```typescript
function IdentityDetail({ identity }: { identity: Identity }) {
  if (!identity.image) return null;

  return (
    <div>
      {/* Thumbnail in sidebar */}
      <aside>
        <img 
          src={identity.image.thumbnail}
          alt="Thumbnail"
          className="w-20 h-20 rounded-full"
        />
      </aside>

      {/* Large image for main view */}
      <main>
        <img 
          src={identity.image.large}
          alt={identity.name}
          className="w-full"
        />
      </main>

      {/* Original for lightbox/modal */}
      <a href={identity.image.original} target="_blank">
        View Full Size
      </a>
    </div>
  );
}
```

### Image Upload

When uploading images through the API:

1. **Upload endpoint**: `PUT /api/v1/identities/{id}/upload-image/`
2. **Content-Type**: `multipart/form-data`
3. **Field name**: `image`
4. **Response**: Returns updated identity with all image sizes

Example:

```typescript
const formData = new FormData();
formData.append('image', imageFile);

const response = await fetch(`/api/v1/identities/${id}/upload-image/`, {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

const identity = await response.json();
// identity.image now contains all sizes
```

## Image Size Guidelines

### When to Use Each Size

- **Thumbnail (100x100)**: 
  - User avatars
  - Small list items
  - Icon-sized displays
  
- **Medium (300x169, 16:9)**:
  - Card components
  - List views
  - Grid layouts
  
- **Large (600x338, 16:9)**:
  - Hero sections
  - Detail page headers
  - Featured content
  
- **Original**:
  - Lightbox/modal views
  - Download links
  - Full-screen displays

### Aspect Ratio Considerations

- **Thumbnail**: Square (1:1) - good for avatars and icons
- **Medium & Large**: 16:9 - matches modern display standards
- Images are automatically cropped/resized to fit these dimensions

## Backend Configuration

### Settings

The image system is configured in `server/settings/common.py`:

```python
VERSATILEIMAGEFIELD_SETTINGS = {
    "create_images_on_demand": True,  # Generate sizes when first accessed
    "jpeg_resize_quality": 70,        # Quality vs file size balance
    "cache_length": 2592000,          # 30 days cache
}
```

### Storage Backend

S3 storage is configured in environment-specific settings:
- `server/settings/local.py`
- `server/settings/staging.py`
- `server/settings/production.py`

Key settings:
- `location: "media"` - All files stored under `/media/` prefix
- No ACLs (bucket policy handles public access)
- Custom domain for S3 URLs

## Troubleshooting

### Images Not Showing

1. **Check API response**: Verify `image` field is not `null`
2. **Check URLs**: Ensure S3 URLs are accessible (no CORS issues)
3. **Check sizes**: First access generates sizes - may take a moment
4. **Check bucket policy**: Ensure public read access is configured

### Sizes Not Generated

1. **First access**: Sizes are generated on first API call
2. **Check logs**: Backend logs will show size generation
3. **Check S3**: Look for files in `__sized__` directory
4. **Verify settings**: Ensure `create_images_on_demand: True`

### Type Errors

If TypeScript complains about image types:
- Ensure `Identity` type uses `ImageSizes | null`
- Check that API response matches `ImageSizes` interface
- Verify imports: `import { ImageSizes } from "@/types/imageSizes"`

## Best Practices

1. **Always check for null**: `if (!identity.image) return null;`
2. **Use appropriate sizes**: Match image size to display context
3. **Lazy loading**: Use `loading="lazy"` for images below the fold
4. **Error handling**: Handle cases where image generation fails
5. **Responsive images**: Use `srcSet` for better performance

## Related Files

- Backend serializer: `server/apps/core/serializers/versatile_image_field_with_sizes.py`
- Backend model: `server/apps/core/models.py` (ImageMixin)
- Frontend types: `client/src/types/imageSizes.ts`
- Frontend types: `client/src/types/identity.ts`
- Settings: `server/settings/common.py` (VersatileImageField config)

