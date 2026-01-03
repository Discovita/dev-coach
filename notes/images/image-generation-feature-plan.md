# Image Generation Feature - Implementation Plan

## Overview

Create an admin-only "Images" tab for generating identity images using Gemini's image generation API. Users can upload reference images of themselves, select a user account (self or test account), select an identity, and generate an image that will be saved to S3.

## Current State (What Already Exists)

### Backend
- **S3 Image Storage**: Already configured via `django-storages` + `boto3` in `server/settings/common.py`
- **Identity Model**: Has `image` field (VersatileImageField) via `ImageMixin` - stores identity images in S3
- **Identity ViewSet**: Has `upload-image` and `delete-image` endpoints
- **Test User ViewSet**: `/api/v1/test-users/{id}/identities/` returns identities for test users
- **User ViewSet**: `/api/v1/users/me/identities/` returns identities for current user
- **Gemini Integration**: Working script in `server/services/gemini/text_and_image_to_image.py`

### Frontend
- **Admin Routes**: `App.tsx` shows admin routes when `isAdmin` is true
- **AdminNavbar**: Links defined in `centerLinks` array
- **Test Page Pattern**: Uses `useTestScenarios()` hook to fetch test users
- **Prompts Page Pattern**: Uses tabs and forms

## Implementation Tasks

### Phase 1: Backend - New Models & Endpoints

#### 1.1 Create Reference Images Model (OPTIONAL - could start simpler)
For MVP, we can skip this and just accept images directly in the generate request. If we want persistent reference images:

```python
# server/apps/reference_images/models.py
class UserReferenceImage(ImageMixin, models.Model):
    """Reference images uploaded by a user for image generation."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reference_images")
    name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created_at"]
```

#### 1.2 Create Image Generation Service
```python
# server/services/image_generation/gemini_service.py
class GeminiImageService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    def generate_identity_image(
        self,
        identity: Identity,
        reference_images: List[Image],  # PIL Images
        additional_prompt: str = "",
    ) -> bytes:
        """Generate an identity image using Gemini."""
        prompt = self._build_prompt(identity, additional_prompt)
        response = self.client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=[prompt, *reference_images],
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE'],
                image_config=types.ImageConfig(
                    aspect_ratio="16:9",
                    image_size="4K"
                ),
            )
        )
        # Extract and return image bytes
        ...
```

#### 1.3 Create Image Generation ViewSet
```python
# server/apps/image_generation/views.py
class ImageGenerationViewSet(viewsets.ViewSet):
    """Admin-only endpoints for generating identity images."""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @action(detail=False, methods=["POST"], url_path="generate")
    def generate(self, request):
        """
        Generate an identity image.
        POST /api/v1/image-generation/generate/
        Body (multipart/form-data):
        - identity_id: UUID of the identity to generate image for
        - user_id: UUID of the user (for test accounts) or "me" for current user
        - reference_images: Up to 5 image files
        - prompt: Additional prompt text (optional)
        
        Returns: { "success": true, "image_url": "...", "identity": {...} }
        """
        ...
    
    @action(detail=False, methods=["GET"], url_path="users")
    def list_users(self, request):
        """
        List available users for image generation (current user + test users).
        GET /api/v1/image-generation/users/
        """
        ...
```

#### 1.4 Register URLs
```python
# server/urls.py or appropriate app urls
router.register(r"image-generation", ImageGenerationViewSet, basename="image-generation")
```

### Phase 2: Frontend - Images Page

#### 2.1 Add Route
```typescript
// App.tsx - Add to admin routes
<Route path="/images" element={<Images />} />
```

#### 2.2 Add Navbar Link
```typescript
// AdminNavbar.tsx
const centerLinks = [
  { label: "Home", to: "/" },
  { label: "Chat", to: "/chat" },
  { label: "Test", to: "/test" },
  { label: "Prompts", to: "/prompts" },
  { label: "Images", to: "/images" },  // NEW
];
```

#### 2.3 Create Images Page
```
client/src/pages/images/
├── Images.tsx              # Main page component
├── components/
│   ├── UserSelector.tsx    # Dropdown to select current user or test user
│   ├── IdentitySelector.tsx # Dropdown to select identity from chosen user
│   ├── ReferenceImageUpload.tsx # Upload up to 5 reference images
│   └── GeneratedImageDisplay.tsx # Show generated image with save option
└── hooks/
    └── use-image-generation.ts # TanStack Query hooks for API calls
```

#### 2.4 Page Layout (Simple MVP)
```
┌─────────────────────────────────────────────────────────────┐
│  [User Selector ▼]  [Identity Selector ▼]                   │
├─────────────────────────────────────────────────────────────┤
│  Reference Images (up to 5)                                 │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                   │
│  │  +  │ │     │ │     │ │     │ │     │                   │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘                   │
├─────────────────────────────────────────────────────────────┤
│  Additional Prompt (optional)                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                                                         ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  [Generate Image]                                           │
├─────────────────────────────────────────────────────────────┤
│  Generated Image                                            │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                                                         ││
│  │                    [Image Preview]                      ││
│  │                                                         ││
│  └─────────────────────────────────────────────────────────┘│
│  [Save to Identity] [Download]                              │
└─────────────────────────────────────────────────────────────┘
```

### Phase 3: API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/image-generation/users/` | List available users (me + test users) |
| GET | `/api/v1/users/me/identities/` | Get current user's identities (existing) |
| GET | `/api/v1/test-users/{id}/identities/` | Get test user's identities (existing) |
| POST | `/api/v1/image-generation/generate/` | Generate image for identity |
| PATCH | `/api/v1/identities/{id}/upload-image/` | Save generated image to identity (existing) |

### Phase 4: Environment Setup

#### 4.1 Add GEMINI_API_KEY to settings
```python
# server/settings/common.py
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
```

#### 4.2 Ensure .env has key
```
GEMINI_API_KEY=your_key_here
```

## Implementation Order

1. **Backend: Image Generation Service** (30 min)
   - Create `server/services/image_generation/gemini_service.py`
   - Port working code from `server/services/gemini/text_and_image_to_image.py`
   - Add to settings

2. **Backend: Image Generation ViewSet** (1 hr)
   - Create `server/apps/image_generation/` app
   - Create ViewSet with `generate` and `list_users` actions
   - Register URLs
   - Test with curl/Postman

3. **Frontend: Basic Page Structure** (30 min)
   - Add route and navbar link
   - Create `Images.tsx` with basic layout
   - Create hooks for API calls

4. **Frontend: User & Identity Selectors** (45 min)
   - Create `UserSelector` component (dropdown with "Me" + test users)
   - Create `IdentitySelector` component (loads identities based on selected user)

5. **Frontend: Reference Image Upload** (45 min)
   - Create `ReferenceImageUpload` component
   - Support up to 5 images
   - Preview thumbnails, remove functionality

6. **Frontend: Generate & Display** (1 hr)
   - Wire up generate button
   - Show loading state (image generation takes time)
   - Display generated image
   - Add "Save to Identity" button (calls existing upload-image endpoint)

## Total Estimated Time: ~4-5 hours

## Files to Create

### Backend
- `server/apps/image_generation/__init__.py`
- `server/apps/image_generation/apps.py`
- `server/apps/image_generation/views.py`
- `server/services/image_generation/__init__.py`
- `server/services/image_generation/gemini_service.py`

### Frontend
- `client/src/pages/images/Images.tsx`
- `client/src/pages/images/components/UserSelector.tsx`
- `client/src/pages/images/components/IdentitySelector.tsx`
- `client/src/pages/images/components/ReferenceImageUpload.tsx`
- `client/src/pages/images/components/GeneratedImageDisplay.tsx`
- `client/src/pages/images/hooks/use-image-generation.ts`
- `client/src/api/imageGeneration.ts`

## Notes

- The Gemini API model `gemini-3-pro-image-preview` is being used for text-and-image-to-image generation
- Images are saved to S3 using `default_storage` which is configured for S3
- Generated images will be saved directly to the Identity model's `image` field using the existing `upload-image` endpoint
- For MVP, reference images are uploaded per-request (not persisted). We can add persistent reference images later if needed.
