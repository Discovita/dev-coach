# Image Generation Feature - Implementation Plan

## Coding Standards

This implementation follows the project's new coding standards:
- **Directory-based organization**: `models/`, `serializers/`, `views/`, `functions/`, `utils/`, `tests/`
- **One function per file**: Each business logic function in its own file with descriptive name
- **Function directories**: `functions/admin/` vs `functions/public/` for access control
- **Thin views**: ViewSets only handle HTTP concerns, delegate to functions
- **Proper exports**: All `__init__.py` files export their contents

Reference: `.cursor/rules/refactor-individual-view.mdc` and `.cursor/rules/how-to-add-a-new-app-to-the-drf-project.mdc`

## Overview

Create an admin-only "Images" tab for generating identity images using Gemini's image generation API. Users can:
1. Select a user account (self or any test account)
2. View/manage reference images stored for that user (up to 5 per user)
3. Select an identity from that user
4. Generate an image using the reference images + identity context
5. Save generated images to S3 and attach to identities

## Current State (What Already Exists)

### Backend
- **S3 Image Storage**: Already configured via `django-storages` + `boto3` in `server/settings/common.py`
- **Identity Model**: Has `image` field (VersatileImageField) via `ImageMixin` - stores identity images in S3
- **Identity ViewSet**: Has `upload-image` and `delete-image` endpoints
- **Test User ViewSet**: `/api/v1/test-users/{id}/identities/` returns identities for test users
- **User ViewSet**: `/api/v1/users/me/identities/` returns identities for current user
- **Gemini Integration**: Working script in `server/services/gemini/text_and_image_to_image.py`
- **ImageMixin**: Base class with VersatileImageField for S3 storage

### Frontend
- **Admin Routes**: `App.tsx` shows admin routes when `isAdmin` is true
- **AdminNavbar**: Links defined in `centerLinks` array
- **Test Page Pattern**: Uses `useTestScenarios()` hook to fetch test users
- **Prompts Page Pattern**: Uses tabs and forms

## Implementation Tasks

### Phase 1: Backend - Reference Images App (New Coding Standards) ✅ COMPLETED

#### 1.1 Create Reference Images App
```bash
cd server/apps/
python ../manage.py startapp reference_images
```

#### 1.2 Set Up Directory Structure (New Standards)
After creating the app, restructure to use directory-based organization:

```
server/apps/reference_images/
├── __init__.py
├── admin.py
├── apps.py                          # Update name to 'apps.reference_images'
├── models/
│   ├── __init__.py                  # Export: from .reference_image import ReferenceImage
│   └── reference_image.py           # Single model file
├── serializers/
│   ├── __init__.py                  # Export: from .reference_image import ReferenceImageSerializer
│   └── reference_image.py           # Single serializer file
├── views/
│   ├── __init__.py                  # Export: from .reference_image_viewset import ReferenceImageViewSet
│   └── reference_image_viewset.py   # Thin viewset
├── functions/
│   ├── __init__.py
│   ├── public/
│   │   ├── __init__.py              # Export all public functions
│   │   ├── create_reference_image.py
│   │   ├── upload_reference_image.py
│   │   └── delete_reference_image.py
│   └── admin/
│       ├── __init__.py              # Export all admin functions
│       └── create_reference_image_for_user.py
├── utils/
│   ├── __init__.py
│   └── get_next_available_order.py
└── tests/
    ├── __init__.py
    ├── test_create_reference_image.py
    ├── test_upload_reference_image.py
    └── test_delete_reference_image.py
```

#### 1.3 Update apps.py
```python
# server/apps/reference_images/apps.py
from django.apps import AppConfig


class ReferenceImagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.reference_images'
```

#### 1.4 Create Model
```python
# server/apps/reference_images/models/reference_image.py
import uuid
from django.db import models
from apps.users.models import User
from apps.core.models import ImageMixin


class ReferenceImage(ImageMixin, models.Model):
    """
    Reference images uploaded by/for a user for AI image generation.
    Each user can have up to 5 reference images.
    These are used as input to Gemini for generating identity images.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="reference_images",
        help_text="The user these reference images belong to"
    )
    name = models.CharField(
        max_length=255, 
        blank=True,
        help_text="Optional name/label for this image (e.g., 'Headshot 1')"
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Display order (0-4)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["order", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "order"],
                name="unique_user_image_order"
            )
        ]
    
    def __str__(self):
        return f"{self.user.email} - Reference Image {self.order + 1}"
```

```python
# server/apps/reference_images/models/__init__.py
from .reference_image import ReferenceImage

__all__ = ["ReferenceImage"]
```

#### 1.5 Create Serializer
```python
# server/apps/reference_images/serializers/reference_image.py
from rest_framework import serializers
from apps.reference_images.models import ReferenceImage
from apps.core.serializers import VersatileImageFieldWithSizes


class ReferenceImageSerializer(serializers.ModelSerializer):
    """Serializer for ReferenceImage model."""
    user = serializers.CharField(source="user_id", read_only=True)
    image = VersatileImageFieldWithSizes(required=False, allow_null=True, read_only=True)
    
    class Meta:
        model = ReferenceImage
        fields = ("id", "user", "name", "order", "image", "created_at", "updated_at")
        read_only_fields = ("id", "user", "created_at", "updated_at")
```

```python
# server/apps/reference_images/serializers/__init__.py
from .reference_image import ReferenceImageSerializer

__all__ = ["ReferenceImageSerializer"]
```

#### 1.6 Create Utility Functions
```python
# server/apps/reference_images/utils/get_next_available_order.py
from typing import Set
from apps.reference_images.models import ReferenceImage
from apps.users.models import User

MAX_REFERENCE_IMAGES = 5


def get_next_available_order(user: User) -> int:
    """
    Get the next available order slot for a user's reference images.
    
    Args:
        user: The user to check for available slots
        
    Returns:
        The next available order number (0-4)
        
    Raises:
        ValueError: If all 5 slots are filled
    """
    existing_orders: Set[int] = set(
        ReferenceImage.objects.filter(user=user).values_list("order", flat=True)
    )
    
    for i in range(MAX_REFERENCE_IMAGES):
        if i not in existing_orders:
            return i
    
    raise ValueError(f"Maximum {MAX_REFERENCE_IMAGES} reference images allowed")
```

```python
# server/apps/reference_images/utils/__init__.py
from .get_next_available_order import get_next_available_order, MAX_REFERENCE_IMAGES

__all__ = ["get_next_available_order", "MAX_REFERENCE_IMAGES"]
```

#### 1.7 Create Business Logic Functions
```python
# server/apps/reference_images/functions/public/create_reference_image.py
from typing import Dict, Any, Optional
from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.reference_images.models import ReferenceImage
from apps.reference_images.utils import get_next_available_order, MAX_REFERENCE_IMAGES
from apps.users.models import User


@transaction.atomic
def create_reference_image(
    user: User,
    name: str = "",
    order: Optional[int] = None,
    image_file: Optional[Any] = None,
) -> ReferenceImage:
    """
    Create a new reference image for a user.
    
    Args:
        user: The user to create the reference image for
        name: Optional name/label for the image
        order: Optional specific order slot (0-4). If not provided, uses next available.
        image_file: Optional image file to upload immediately
        
    Returns:
        The created ReferenceImage instance
        
    Raises:
        ValidationError: If user has reached maximum images or order is invalid
    """
    # Check limit
    existing_count = ReferenceImage.objects.filter(user=user).count()
    if existing_count >= MAX_REFERENCE_IMAGES:
        raise ValidationError(f"Maximum {MAX_REFERENCE_IMAGES} reference images allowed")
    
    # Determine order
    if order is None:
        order = get_next_available_order(user)
    elif order < 0 or order >= MAX_REFERENCE_IMAGES:
        raise ValidationError(f"Order must be between 0 and {MAX_REFERENCE_IMAGES - 1}")
    elif ReferenceImage.objects.filter(user=user, order=order).exists():
        raise ValidationError(f"Order {order} is already in use")
    
    # Create the reference image
    ref_image = ReferenceImage.objects.create(
        user=user,
        name=name,
        order=order,
    )
    
    # Upload image if provided
    if image_file:
        ref_image.image = image_file
        ref_image.save()
    
    return ref_image
```

```python
# server/apps/reference_images/functions/public/upload_reference_image.py
from typing import Any
from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.reference_images.models import ReferenceImage


@transaction.atomic
def upload_reference_image(
    reference_image: ReferenceImage,
    image_file: Any,
) -> ReferenceImage:
    """
    Upload or replace the image file for a reference image.
    
    Args:
        reference_image: The ReferenceImage instance to update
        image_file: The new image file to upload
        
    Returns:
        The updated ReferenceImage instance
        
    Raises:
        ValidationError: If no image file provided
    """
    if not image_file:
        raise ValidationError("No image file provided")
    
    # Delete old image if exists
    if reference_image.image:
        reference_image.image.delete()
    
    reference_image.image = image_file
    reference_image.save()
    
    return reference_image
```

```python
# server/apps/reference_images/functions/public/delete_reference_image.py
from django.db import transaction
from apps.reference_images.models import ReferenceImage


@transaction.atomic
def delete_reference_image(reference_image: ReferenceImage) -> None:
    """
    Delete a reference image and its associated file.
    
    Args:
        reference_image: The ReferenceImage instance to delete
    """
    # Delete the image file if it exists
    if reference_image.image:
        reference_image.image.delete()
    
    reference_image.delete()
```

```python
# server/apps/reference_images/functions/public/__init__.py
from .create_reference_image import create_reference_image
from .upload_reference_image import upload_reference_image
from .delete_reference_image import delete_reference_image

__all__ = [
    "create_reference_image",
    "upload_reference_image",
    "delete_reference_image",
]
```

```python
# server/apps/reference_images/functions/admin/create_reference_image_for_user.py
from typing import Any, Optional
from uuid import UUID
from django.db import transaction
from rest_framework.exceptions import NotFound
from apps.reference_images.models import ReferenceImage
from apps.reference_images.functions.public import create_reference_image
from apps.users.models import User


@transaction.atomic
def create_reference_image_for_user(
    user_id: UUID,
    name: str = "",
    order: Optional[int] = None,
    image_file: Optional[Any] = None,
) -> ReferenceImage:
    """
    Admin function to create a reference image for any user by ID.
    
    Args:
        user_id: UUID of the target user
        name: Optional name/label for the image
        order: Optional specific order slot (0-4)
        image_file: Optional image file to upload immediately
        
    Returns:
        The created ReferenceImage instance
        
    Raises:
        NotFound: If user does not exist
        ValidationError: If user has reached maximum images
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise NotFound(f"User {user_id} not found")
    
    return create_reference_image(
        user=user,
        name=name,
        order=order,
        image_file=image_file,
    )
```

```python
# server/apps/reference_images/functions/admin/__init__.py
from .create_reference_image_for_user import create_reference_image_for_user

__all__ = ["create_reference_image_for_user"]
```

```python
# server/apps/reference_images/functions/__init__.py
from . import public
from . import admin

__all__ = ["public", "admin"]
```

#### 1.8 Create Thin ViewSet
```python
# server/apps/reference_images/views/reference_image_viewset.py
"""
ViewSet for Reference Images CRUD operations.
Thin view layer - delegates all business logic to functions.
"""
from rest_framework import viewsets, status, decorators
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import logging

from apps.reference_images.models import ReferenceImage
from apps.reference_images.serializers import ReferenceImageSerializer
from apps.reference_images.functions.public import (
    create_reference_image,
    upload_reference_image,
    delete_reference_image,
)
from apps.reference_images.functions.admin import create_reference_image_for_user

log = logging.getLogger(__name__)


class ReferenceImageViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for reference images.
    Admin users can manage reference images for any user.
    Regular users can only manage their own reference images.
    
    Endpoints:
    - GET /api/v1/reference-images/?user_id={uuid} - List reference images for a user
    - POST /api/v1/reference-images/ - Create new reference image
    - GET /api/v1/reference-images/{id}/ - Get single reference image
    - PATCH /api/v1/reference-images/{id}/ - Update reference image
    - DELETE /api/v1/reference-images/{id}/ - Delete reference image
    - POST /api/v1/reference-images/{id}/upload-image/ - Upload/replace image file
    """
    serializer_class = ReferenceImageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_queryset(self):
        """Filter by user_id query param or default to current user."""
        user_id = self.request.query_params.get("user_id")
        if user_id and self.request.user.is_staff:
            return ReferenceImage.objects.filter(user_id=user_id)
        return ReferenceImage.objects.filter(user=self.request.user)
    
    def create(self, request: Request, *args, **kwargs) -> Response:
        """Create a new reference image."""
        user_id = request.data.get("user_id")
        
        # Admin creating for another user
        if user_id and request.user.is_staff:
            ref_image = create_reference_image_for_user(
                user_id=user_id,
                name=request.data.get("name", ""),
                order=request.data.get("order"),
                image_file=request.FILES.get("image"),
            )
        else:
            # User creating for themselves
            ref_image = create_reference_image(
                user=request.user,
                name=request.data.get("name", ""),
                order=request.data.get("order"),
                image_file=request.FILES.get("image"),
            )
        
        return Response(
            ReferenceImageSerializer(ref_image).data,
            status=status.HTTP_201_CREATED
        )
    
    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """Delete a reference image."""
        ref_image = self.get_object()
        delete_reference_image(ref_image)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @decorators.action(detail=True, methods=["POST"], url_path="upload-image")
    def upload_image(self, request: Request, pk=None) -> Response:
        """Upload or replace the image file for a reference image."""
        ref_image = self.get_object()
        
        updated = upload_reference_image(
            reference_image=ref_image,
            image_file=request.FILES.get("image"),
        )
        
        return Response(ReferenceImageSerializer(updated).data)
```

```python
# server/apps/reference_images/views/__init__.py
from .reference_image_viewset import ReferenceImageViewSet

__all__ = ["ReferenceImageViewSet"]
```

#### 1.9 Register App and URLs
```python
# server/settings/common.py - Add to INSTALLED_APPS
"apps.reference_images",

# server/urls.py - Add to router
from apps.reference_images.views import ReferenceImageViewSet
router.register(r"reference-images", ReferenceImageViewSet, basename="reference-images")
```

#### 1.10 Create Migrations
```bash
cd server
source ../.venv/bin/activate
python manage.py makemigrations reference_images
python manage.py migrate
```

### Phase 2: Backend - Image Generation App (New Coding Standards)

#### Prompt Construction Architecture - Using Existing PromptManager

Rather than creating a standalone `build_identity_prompt.py` utility, we'll integrate with the **existing `prompt_manager` service** which already provides:

- **Context gathering** - Functions that format identity data for prompts
- **Database-stored templates** - Versioned prompts with `required_context_keys`
- **Extensible pattern** - Just add new `ContextKey` values and context functions

**Integration Approach:**

1. **Add new PromptType** - `IMAGE_GENERATION` in `enums/prompt_type.py`
2. **Add new ContextKey** - `IMAGE_IDENTITY` in `enums/context_keys.py`
3. **Create context function** - `get_identity_context_for_image()` that formats identity for image generation
4. **Store prompt template in DB** - Create Prompt record with the image generation template
5. **Add method to PromptManager** - `create_image_generation_prompt(identity, additional_prompt)`

**Why use PromptManager?**
- **Consistency** - Same pattern as chat prompts
- **Versioning** - Prompt templates stored in DB with version control
- **Iteration** - Update prompts without code changes via admin/API
- **Context reuse** - Leverage existing identity formatting functions
- **Testability** - Same testing patterns as existing prompts

**Data Flow:**
```
┌─────────────────────────────────────────────────────────────────────┐
│  generate_identity_image() function                                  │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ 1. Fetch Identity from database                                 ││
│  │ 2. Fetch ReferenceImages for user                               ││
│  │ 3. Call PromptManager.create_image_generation_prompt(identity)  ││
│  │    └─> Fetches prompt template from DB                          ││
│  │    └─> Gathers context using get_identity_context_for_image()       ││
│  │    └─> Returns formatted prompt string                          ││
│  │ 4. Call load_pil_images_from_references(reference_images)       ││
│  │    └─> Returns: [PIL.Image, PIL.Image, ...]                     ││
│  │ 5. Call GeminiImageService.generate_image(prompt, pil_images)   ││
│  │    └─> Returns: bytes (PNG image data)                          ││
│  │ 6. Save to S3 and return URL                                    ││
│  └─────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

**Key Differences from Chat Prompts:**
- Takes `Identity` directly (not from CoachState)
- Returns just a string (no response_format model)
- No action instructions or message history needed
- Simpler context gathering (identity fields only)

#### 2.1 Create Image Generation App
```bash
cd server/apps/
python ../manage.py startapp image_generation
```

#### 2.2 Set Up Directory Structure
```
server/apps/image_generation/
├── __init__.py
├── apps.py                           # Update name to 'apps.image_generation'
├── views/
│   ├── __init__.py                   # Export: from .image_generation_viewset import ImageGenerationViewSet
│   └── image_generation_viewset.py   # Thin viewset
├── functions/
│   ├── __init__.py
│   └── admin/
│       ├── __init__.py
│       ├── list_available_users.py
│       ├── generate_identity_image.py
│       └── save_image_to_identity.py
├── utils/
│   ├── __init__.py
│   └── load_pil_images_from_references.py   # NOTE: build_identity_prompt moved to prompt_manager
└── tests/
    ├── __init__.py
    ├── test_generate_identity_image.py
    └── test_list_available_users.py
```

#### 2.3 Integrate with PromptManager

##### Step 1: Add new PromptType
```python
# enums/prompt_type.py - Add new type
class PromptType(str, Enum):
    COACH = "coach"
    SENTINEL = "sentinel"
    IMAGE_GENERATION = "image_generation"  # NEW
```

##### Step 2: Add new ContextKey
```python
# enums/context_keys.py - Add new key
class ContextKey(str, Enum):
    # ... existing keys ...
    IMAGE_IDENTITY = "image_identity"  # NEW - Identity data for image generation
```

##### Step 3: Create context function
```python
# server/services/prompt_manager/utils/context/func/get_identity_context_for_image.py
from apps.identities.models import Identity
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


def get_identity_context_for_image(identity: Identity) -> str:
    """
    Format identity data for image generation prompts.
    
    Unlike get_current_identity_context which uses CoachState,
    this takes an Identity directly for image generation use cases.
    
    Args:
        identity: The Identity model instance to format
        
    Returns:
        Formatted string with identity details for image generation
    """
    parts = [
        f'Identity Name: "{identity.name}"',
        f"Category: {identity.category}",
    ]
    
    if identity.i_am_statement:
        parts.append(f"I Am Statement: {identity.i_am_statement}")
    
    if identity.visualization:
        parts.append(f"Visualization: {identity.visualization}")
    
    if identity.notes:
        notes_str = "; ".join(identity.notes)
        parts.append(f"Notes: {notes_str}")
    
    return "\n".join(parts)
```

##### Step 4: Add method to PromptManager
```python
# server/services/prompt_manager/manager.py - Add new method

def create_image_generation_prompt(
    self, 
    identity: "Identity", 
    additional_prompt: str = ""
) -> str:
    """
    Create a prompt for identity image generation.
    
    Unlike chat prompts, this:
    - Takes an Identity directly (not from CoachState)
    - Returns just a string (no response_format model)
    - Uses a simpler context gathering flow
    
    Args:
        identity: The Identity to generate an image for
        additional_prompt: Optional extra instructions from admin
        
    Returns:
        Formatted prompt string for Gemini
    """
    # Fetch the latest active image generation prompt
    prompt = (
        Prompt.objects.filter(
            prompt_type=PromptType.IMAGE_GENERATION, 
            is_active=True
        )
        .order_by("-version")
        .first()
    )
    
    if not prompt:
        raise ValueError("No active image generation prompt found")
    
    log.info(f"Using Image Generation Prompt version: {prompt.version}")
    
    # Gather identity context
    from services.prompt_manager.utils.context.func.get_identity_context_for_image import (
        get_identity_context_for_image
    )
    identity_context = get_identity_context_for_image(identity)
    
    # Format the prompt template with context
    formatted_prompt = prompt.body.format(
        identity_context=identity_context,
        additional_prompt=additional_prompt or "None provided",
    )
    
    return formatted_prompt
```

##### Step 5: Create prompt template in database
Create a new Prompt record (via admin or migration):

```python
# Example prompt body (stored in DB)
"""
We're creating an Identity Image for this person.

{identity_context}

Create a professional, confident, and inspiring image for this Identity.
It is critical that the person's face remains intact and recognizable.
The image should be an ideal visualization of them living as this Identity.
Give it a movie poster quality aesthetic.
Nothing negative should be conveyed - this is an aspirational image.

Additional instructions: {additional_prompt}
"""
```

#### 2.3 Create Image Generation Service (in server/services/)
```python
# server/services/image_generation/__init__.py
from .gemini_service import GeminiImageService

__all__ = ["GeminiImageService"]
```

```python
# server/services/image_generation/gemini_service.py
"""
Gemini Image Generation Service.
Wrapper around the Google Gemini API for generating images.
"""
from google import genai
from google.genai import types
from django.conf import settings
from PIL import Image
from io import BytesIO
from typing import List
import logging

log = logging.getLogger(__name__)


class GeminiImageService:
    """Service for generating images using Google Gemini API."""
    
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    def generate_image(
        self,
        prompt: str,
        reference_images: List[Image.Image],
        aspect_ratio: str = "16:9",
        resolution: str = "4K",
    ) -> bytes:
        """
        Generate an image using Gemini.
        
        Args:
            prompt: The text prompt for image generation
            reference_images: List of PIL Image objects as reference
            aspect_ratio: One of "1:1","2:3","3:2","3:4","4:3","4:5","5:4","9:16","16:9","21:9"
            resolution: One of "1K", "2K", "4K"
        
        Returns:
            Image bytes (PNG format)
            
        Raises:
            ValueError: If no image is generated in response
        """
        contents = [prompt] + reference_images
        
        response = self.client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE'],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=resolution
                ),
            )
        )
        
        # Extract image from response
        for part in response.parts:
            if part.inline_data is not None:
                image = part.as_image()
                buffer = BytesIO()
                image.save(buffer, format="PNG")
                return buffer.getvalue()
        
        raise ValueError("No image generated in response")
```

#### 2.4 Create Utility Functions

##### load_pil_images_from_references.py

This utility loads PIL Image objects from S3-stored reference images.

```python
# server/apps/image_generation/utils/load_pil_images_from_references.py
from typing import List
from PIL import Image
from apps.reference_images.models import ReferenceImage
import logging

log = logging.getLogger(__name__)


def load_pil_images_from_references(reference_images: List[ReferenceImage]) -> List[Image.Image]:
    """
    Load PIL Image objects from ReferenceImage model instances.
    
    Args:
        reference_images: QuerySet or list of ReferenceImage instances
        
    Returns:
        List of PIL Image objects that could be loaded
        
    Note:
        Images that fail to load are logged and skipped
    """
    pil_images = []
    
    for ref_img in reference_images:
        try:
            img = Image.open(ref_img.image)
            pil_images.append(img)
        except Exception as e:
            log.warning(f"Could not load reference image {ref_img.id}: {e}")
    
    return pil_images
```

```python
# server/apps/image_generation/utils/__init__.py
from .load_pil_images_from_references import load_pil_images_from_references

__all__ = ["load_pil_images_from_references"]
```

#### 2.5 Create Business Logic Functions
```python
# server/apps/image_generation/functions/admin/list_available_users.py
from typing import List, Dict, Any
from apps.users.models import User
from apps.test_scenario.models import TestScenario


def list_available_users(current_user: User) -> List[Dict[str, Any]]:
    """
    List available users for image generation.
    Returns current user + all test scenario users.
    
    Args:
        current_user: The currently authenticated admin user
        
    Returns:
        List of user dictionaries with id, email, name, and type flags
    """
    users = []
    
    # Add current user
    users.append({
        "id": str(current_user.id),
        "email": current_user.email,
        "name": f"{current_user.first_name} {current_user.last_name}".strip() or current_user.email,
        "is_current_user": True,
        "is_test_user": False,
    })
    
    # Add test scenario users
    test_scenarios = TestScenario.objects.select_related("user").all()
    for scenario in test_scenarios:
        if scenario.user:
            users.append({
                "id": str(scenario.user.id),
                "email": scenario.user.email,
                "name": scenario.name,
                "is_current_user": False,
                "is_test_user": True,
            })
    
    return users
```

##### generate_identity_image.py

This is the **orchestration function** that ties everything together. It:
1. Fetches the identity and reference images from the database
2. **Constructs the prompt** using `PromptManager.create_image_generation_prompt()`
3. **Injects the prompt** into the Gemini service
4. Saves the result to S3

```python
# server/apps/image_generation/functions/admin/generate_identity_image.py
from typing import Dict, Any
from uuid import UUID
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.exceptions import NotFound, ValidationError
import uuid
import logging

from apps.identities.models import Identity
from apps.reference_images.models import ReferenceImage
from apps.image_generation.utils import load_pil_images_from_references
from services.image_generation import GeminiImageService
from services.prompt_manager import PromptManager  # Use existing prompt manager

log = logging.getLogger(__name__)


def generate_identity_image(
    identity_id: UUID,
    user_id: UUID,
    additional_prompt: str = "",
) -> Dict[str, Any]:
    """
    Generate an identity image using stored reference images.
    
    This function orchestrates the prompt/generation flow:
    1. FETCH: Get identity and reference images from database
    2. CONSTRUCT: Build prompt using PromptManager (DB-stored template)
    3. GENERATE: Pass prompt to GeminiImageService
    4. SAVE: Store result in S3
    
    The PromptManager handles prompt construction using the same pattern
    as chat prompts - templates stored in DB with context injection.
    
    Args:
        identity_id: UUID of the identity to generate image for
        user_id: UUID of the user whose reference images to use
        additional_prompt: Extra prompt text from admin (optional)
        
    Returns:
        Dictionary containing:
            - success: bool
            - image_url: S3 URL of generated image
            - image_bytes: Raw image bytes (for saving to identity)
            - prompt_used: The constructed prompt (for debugging/logging)
            
    Raises:
        NotFound: If identity not found
        ValidationError: If no reference images available
    """
    # ===== STEP 1: Fetch data from database =====
    try:
        identity = Identity.objects.get(id=identity_id)
    except Identity.DoesNotExist:
        raise NotFound("Identity not found")
    
    reference_images = ReferenceImage.objects.filter(
        user_id=user_id
    ).exclude(image="").exclude(image__isnull=True)
    
    if not reference_images.exists():
        raise ValidationError("No reference images found for this user")
    
    # ===== STEP 2: Prepare inputs =====
    pil_images = load_pil_images_from_references(reference_images)
    
    if not pil_images:
        raise ValidationError("Could not load any reference images")
    
    # ===== STEP 3: CONSTRUCT prompt using PromptManager =====
    # Uses the existing prompt_manager pattern with DB-stored templates
    prompt_manager = PromptManager()
    prompt = prompt_manager.create_image_generation_prompt(identity, additional_prompt)
    log.info(f"Constructed prompt for identity {identity.name}: {len(prompt)} chars")
    
    # ===== STEP 4: GENERATE image =====
    service = GeminiImageService()
    image_bytes = service.generate_image(
        prompt=prompt,
        reference_images=pil_images,
    )
    
    # ===== STEP 5: Save to S3 =====
    filename = f"{uuid.uuid4()}.png"
    path = f"generated_images/{filename}"
    saved_path = default_storage.save(path, ContentFile(image_bytes))
    image_url = default_storage.url(saved_path)
    
    return {
        "success": True,
        "image_url": image_url,
        "image_bytes": image_bytes,
        "filename": filename,
        "prompt_used": prompt,  # For debugging/logging
    }
```

```python
# server/apps/image_generation/functions/admin/save_image_to_identity.py
from uuid import UUID
from django.core.files.base import ContentFile
from rest_framework.exceptions import NotFound

from apps.identities.models import Identity


def save_image_to_identity(
    identity_id: UUID,
    image_bytes: bytes,
    filename: str,
) -> Identity:
    """
    Save generated image bytes to an identity's image field.
    
    Args:
        identity_id: UUID of the identity to update
        image_bytes: Raw image bytes to save
        filename: Filename for the saved image
        
    Returns:
        The updated Identity instance
        
    Raises:
        NotFound: If identity not found
    """
    try:
        identity = Identity.objects.get(id=identity_id)
    except Identity.DoesNotExist:
        raise NotFound("Identity not found")
    
    identity.image.save(filename, ContentFile(image_bytes))
    identity.save()
    
    return identity
```

```python
# server/apps/image_generation/functions/admin/__init__.py
from .list_available_users import list_available_users
from .generate_identity_image import generate_identity_image
from .save_image_to_identity import save_image_to_identity

__all__ = [
    "list_available_users",
    "generate_identity_image",
    "save_image_to_identity",
]
```

```python
# server/apps/image_generation/functions/__init__.py
from . import admin

__all__ = ["admin"]
```

#### 2.6 Create Thin ViewSet
```python
# server/apps/image_generation/views/image_generation_viewset.py
"""
ViewSet for Identity Image Generation.
Admin-only endpoints. Thin view layer - delegates to functions.
"""
from rest_framework import viewsets, status, decorators
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import logging

from apps.identities.serializers import IdentitySerializer
from apps.image_generation.functions.admin import (
    list_available_users,
    generate_identity_image,
    save_image_to_identity,
)

log = logging.getLogger(__name__)


class ImageGenerationViewSet(viewsets.ViewSet):
    """
    Admin-only endpoints for generating identity images.
    
    Endpoints:
    - GET /api/v1/image-generation/users/ - List available users
    - POST /api/v1/image-generation/generate/ - Generate image for identity
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    @decorators.action(detail=False, methods=["GET"], url_path="users")
    def list_users(self, request: Request) -> Response:
        """List available users for image generation."""
        users = list_available_users(request.user)
        return Response(users)
    
    @decorators.action(detail=False, methods=["POST"], url_path="generate")
    def generate(self, request: Request) -> Response:
        """
        Generate an identity image using stored reference images.
        
        POST /api/v1/image-generation/generate/
        Body (JSON):
        - identity_id: UUID of the identity to generate image for
        - user_id: UUID of the user whose reference images to use
        - additional_prompt: Extra prompt text (optional)
        - save_to_identity: Whether to save directly to identity (default: false)
        """
        identity_id = request.data.get("identity_id")
        user_id = request.data.get("user_id")
        additional_prompt = request.data.get("additional_prompt", "")
        should_save = request.data.get("save_to_identity", False)
        
        # Generate the image
        result = generate_identity_image(
            identity_id=identity_id,
            user_id=user_id,
            additional_prompt=additional_prompt,
        )
        
        response_data = {
            "success": result["success"],
            "image_url": result["image_url"],
        }
        
        # Optionally save to identity
        if should_save:
            identity = save_image_to_identity(
                identity_id=identity_id,
                image_bytes=result["image_bytes"],
                filename=result["filename"],
            )
            response_data["identity"] = IdentitySerializer(identity).data
        
        return Response(response_data)
```

```python
# server/apps/image_generation/views/__init__.py
from .image_generation_viewset import ImageGenerationViewSet

__all__ = ["ImageGenerationViewSet"]
```

#### 2.7 Update apps.py
```python
# server/apps/image_generation/apps.py
from django.apps import AppConfig


class ImageGenerationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.image_generation'
```

#### 2.8 Register App and URLs
```python
# server/settings/common.py - Add to INSTALLED_APPS
"apps.image_generation",

# server/urls.py - Add to router
from apps.image_generation.views import ImageGenerationViewSet
router.register(r"image-generation", ImageGenerationViewSet, basename="image-generation")
```

### Phase 3: Frontend - Images Page

#### 3.1 Add Route
```typescript
// App.tsx - Add to admin routes
<Route path="/images" element={<Images />} />
```

#### 3.2 Add Navbar Link
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

#### 3.3 Create Images Page Structure
```
client/src/pages/images/
├── Images.tsx                    # Main page component
├── components/
│   ├── UserSelector.tsx          # Dropdown to select current user or test user
│   ├── IdentitySelector.tsx      # Dropdown to select identity from chosen user
│   ├── ReferenceImageManager.tsx # CRUD for reference images (shows stored images)
│   ├── ReferenceImageSlot.tsx    # Single slot for upload/display/delete
│   └── GeneratedImageDisplay.tsx # Show generated image with save option
├── hooks/
│   ├── use-image-generation.ts   # TanStack Query hooks for generation API
│   └── use-reference-images.ts   # TanStack Query hooks for reference images CRUD
└── api/
    ├── imageGeneration.ts        # API calls for image generation
    └── referenceImages.ts        # API calls for reference images CRUD
```

#### 3.4 Page Layout (MVP)
```
┌─────────────────────────────────────────────────────────────┐
│  [User Selector ▼]                                          │
├─────────────────────────────────────────────────────────────┤
│  Reference Images for [Selected User] (up to 5)             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐│
│  │ [img]   │ │ [img]   │ │   +     │ │   +     │ │   +     ││
│  │ [🗑️]    │ │ [🗑️]    │ │ upload  │ │ upload  │ │ upload  ││
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘│
├─────────────────────────────────────────────────────────────┤
│  [Identity Selector ▼]                                      │
│  Selected: "Creative Visionary" - "I am a creative..."      │
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
│  [Save to Identity] [Download] [Regenerate]                 │
└─────────────────────────────────────────────────────────────┘
```

#### 3.5 Reference Image Management Component
```typescript
// client/src/pages/images/components/ReferenceImageManager.tsx
interface ReferenceImageManagerProps {
  userId: string;
}

export function ReferenceImageManager({ userId }: ReferenceImageManagerProps) {
  const { data: images, refetch } = useReferenceImages(userId);
  const uploadMutation = useUploadReferenceImage();
  const deleteMutation = useDeleteReferenceImage();
  
  // Show 5 slots - filled with images or empty for upload
  const slots = Array.from({ length: 5 }, (_, i) => {
    const image = images?.find(img => img.order === i);
    return { order: i, image };
  });
  
  return (
    <div className="grid grid-cols-5 gap-4">
      {slots.map(slot => (
        <ReferenceImageSlot
          key={slot.order}
          order={slot.order}
          image={slot.image}
          userId={userId}
          onUpload={(file) => uploadMutation.mutate({ userId, order: slot.order, file })}
          onDelete={() => deleteMutation.mutate(slot.image.id)}
        />
      ))}
    </div>
  );
}
```

### Phase 4: API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| **Reference Images** |||
| GET | `/api/v1/reference-images/?user_id={uuid}` | List reference images for a user |
| POST | `/api/v1/reference-images/` | Create new reference image slot |
| POST | `/api/v1/reference-images/{id}/upload-image/` | Upload image file to slot |
| PATCH | `/api/v1/reference-images/{id}/` | Update reference image metadata |
| DELETE | `/api/v1/reference-images/{id}/` | Delete reference image |
| **Image Generation** |||
| GET | `/api/v1/image-generation/users/` | List available users (me + test users) |
| POST | `/api/v1/image-generation/generate/` | Generate image for identity |
| **Existing Endpoints** |||
| GET | `/api/v1/users/me/identities/` | Get current user's identities |
| GET | `/api/v1/test-users/{id}/identities/` | Get test user's identities |
| PATCH | `/api/v1/identities/{id}/upload-image/` | Save generated image to identity |

### Phase 5: Environment Setup

#### 5.1 Add GEMINI_API_KEY to settings
```python
# server/settings/common.py
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
```

#### 5.2 Ensure .env has key
```
GEMINI_API_KEY=your_key_here
```

## Implementation Order

### Backend Implementation

1. ✅ **Reference Images App - Setup** (15 min) - COMPLETED
   - Create app: `cd server/apps && python ../manage.py startapp reference_images`
   - Create directory structure (models/, serializers/, views/, functions/, utils/, tests/)
   - Update `apps.py` with correct name
   - Register in `settings/common.py` INSTALLED_APPS

2. ✅ **Reference Images App - Model & Serializer** (30 min) - COMPLETED
   - Create `models/reference_image.py`
   - Create `models/__init__.py`
   - Create `serializers/reference_image.py`
   - Create `serializers/__init__.py`
   - Run migrations

3. ✅ **Reference Images App - Functions & Utils** (45 min) - COMPLETED
   - Create `utils/get_next_available_order.py`
   - Create `functions/public/create_reference_image.py`
   - Create `functions/public/upload_reference_image.py`
   - Create `functions/public/delete_reference_image.py`
   - Create `functions/admin/create_reference_image_for_user.py`
   - Create all `__init__.py` exports

4. ✅ **Reference Images App - ViewSet & Tests** (30 min) - COMPLETED
   - Create `views/reference_image_viewset.py` (thin, delegates to functions)
   - Create `views/__init__.py`
   - Register in `urls.py`
   - Created comprehensive test suite (45 tests, all passing)
   - Added API documentation (`docs/docs/api/endpoints/reference-images.md`)
   - Added model documentation (`docs/docs/database/models/reference-image.md`)

5. ✅ **PromptManager Integration** (30 min) - COMPLETED
   - Added `IMAGE_GENERATION` to `enums/prompt_type.py`
   - Added `IDENTITY_FOR_IMAGE` to `enums/context_keys.py`
   - Created `services/prompt_manager/utils/context/func/get_identity_context_for_image.py`
   - Updated `services/prompt_manager/utils/context/func/__init__.py` exports
   - Added `identity_for_image` field to `services/prompt_manager/models/prompt_context.py`
   - Updated `services/prompt_manager/utils/context/get_context_value.py` for new key
   - Updated `services/prompt_manager/utils/context_logging.py` for new key
   - Added `create_image_generation_prompt()` method to `PromptManager`
   - Created management command `seed_image_generation_prompt.py`
   - Seeded Image Generation Prompt v1 into database
   - **BONUS**: Updated frontend Prompts page to show Image Generation & Sentinel tabs
   - **BONUS**: Added `prompt_types` to `/api/v1/core/enums` endpoint

6. ✅ **Image Generation Service** (30 min) - COMPLETED
   - Created `server/services/image_generation/__init__.py`
   - Created `server/services/image_generation/gemini_service.py` with `GeminiImageService` class
   - Ported logic from `server/services/gemini/text_and_image_to_image.py`
   - `GEMINI_API_KEY` already in .env (reads via `os.getenv()`)

7. **Image Generation App - Setup** (15 min)
   - Create app: `cd server/apps && python ../manage.py startapp image_generation`
   - Create directory structure (views/, functions/, utils/, tests/)
   - Update `apps.py` with correct name
   - Register in `settings/common.py` INSTALLED_APPS

8. **Image Generation App - Functions & Utils** (30 min)
   - Create `utils/load_pil_images_from_references.py`
   - Create `functions/admin/list_available_users.py`
   - Create `functions/admin/generate_identity_image.py` (uses PromptManager)
   - Create `functions/admin/save_image_to_identity.py`
   - Create all `__init__.py` exports

9. **Image Generation App - ViewSet** (30 min)
   - Create `views/image_generation_viewset.py` (thin, delegates to functions)
   - Create `views/__init__.py`
   - Register in `urls.py`
   - Test with curl/Postman

### Frontend Implementation

10. **Frontend: API Layer** (30 min)
    - Create `client/src/api/referenceImages.ts`
    - Create `client/src/api/imageGeneration.ts`
    - Create TanStack Query hooks

11. **Frontend: Basic Page Structure** (30 min)
    - Add route and navbar link
    - Create `Images.tsx` with basic layout
    - Create `UserSelector` component

12. **Frontend: Reference Image Manager** (1 hr)
    - Create `ReferenceImageManager` component
    - Create `ReferenceImageSlot` component
    - Wire up upload, delete, display

13. **Frontend: Identity Selection & Generation** (1 hr)
    - Create `IdentitySelector` component
    - Wire up generate button with loading state
    - Create `GeneratedImageDisplay` component
    - Add "Save to Identity" functionality

## Total Estimated Time: ~7-8 hours

## Progress Summary

| Phase | Status | Notes |
|-------|--------|-------|
| Reference Images App | ✅ COMPLETE | 45 tests passing, docs added |
| PromptManager Integration | ✅ COMPLETE | Enums, context function, manager method, seed command, frontend tabs |
| Image Generation Service | ✅ COMPLETE | GeminiImageService with generate_image() and generate_image_bytes() |
| Image Generation App | ⏳ Pending | ViewSet, functions, utils |
| Frontend: API Layer | ⏳ Pending | |
| Frontend: Page Structure | ⏳ Pending | |
| Frontend: Reference Image Manager | ⏳ Pending | |
| Frontend: Identity Selection & Generation | ⏳ Pending | |

## Files to Create

### Backend - Reference Images App ✅ COMPLETED
```
server/apps/reference_images/
├── __init__.py
├── admin.py
├── apps.py
├── migrations/
│   ├── __init__.py
│   └── 0001_initial.py
├── models/
│   ├── __init__.py
│   └── reference_image.py
├── serializers/
│   ├── __init__.py
│   └── reference_image.py
├── views/
│   ├── __init__.py
│   └── reference_image_viewset.py
├── functions/
│   ├── __init__.py
│   ├── public/
│   │   ├── __init__.py
│   │   ├── create_reference_image.py
│   │   ├── upload_reference_image.py
│   │   └── delete_reference_image.py
│   └── admin/
│       ├── __init__.py
│       └── create_reference_image_for_user.py
├── utils/
│   ├── __init__.py
│   └── get_next_available_order.py
└── tests/
    ├── __init__.py
    ├── test_get_next_available_order.py
    ├── test_create_reference_image.py
    ├── test_upload_reference_image.py
    ├── test_delete_reference_image.py
    ├── test_create_reference_image_for_user.py
    └── test_reference_image_viewset.py
```

**Also created:**
- `docs/docs/api/endpoints/reference-images.md` - API documentation
- `docs/docs/database/models/reference-image.md` - Model documentation
- Updated `docs/sidebars.ts` with new doc entries

### Backend - PromptManager Additions ✅ COMPLETED
```
# Updates to existing prompt_manager service
server/services/prompt_manager/
├── manager.py                              # Added create_image_generation_prompt() method
├── models/prompt_context.py                # Added identity_for_image field
└── utils/
    ├── context_logging.py                  # Added IDENTITY_FOR_IMAGE logging
    └── context/
        ├── get_context_value.py            # Added IDENTITY_FOR_IMAGE handler
        └── func/
            ├── __init__.py                 # Updated exports
            └── get_identity_context_for_image.py  # NEW - Format identity for image prompts

# Enum additions
enums/
├── prompt_type.py               # Added IMAGE_GENERATION
└── context_keys.py              # Added IDENTITY_FOR_IMAGE

# Database seed command & data
server/apps/prompts/management/commands/
└── seed_image_generation_prompt.py   # NEW - Seeds Image Generation Prompt v1

# Frontend additions (bonus)
server/apps/core/views.py        # Added prompt_types to enums endpoint
client/src/types/prompt.ts       # Added prompt_type field
client/src/pages/prompts/Prompts.tsx           # Added Image Generation & Sentinel tabs
client/src/pages/prompts/components/NewPromptForm.tsx  # Added prompt_type selector
```

### Backend - Image Generation App
```
server/apps/image_generation/
├── __init__.py
├── apps.py
├── views/
│   ├── __init__.py
│   └── image_generation_viewset.py
├── functions/
│   ├── __init__.py
│   └── admin/
│       ├── __init__.py
│       ├── list_available_users.py
│       ├── generate_identity_image.py   # Uses PromptManager
│       └── save_image_to_identity.py
├── utils/
│   ├── __init__.py
│   └── load_pil_images_from_references.py
└── tests/
    ├── __init__.py
    ├── test_generate_identity_image.py
    └── test_list_available_users.py
```

### Backend - Gemini Service ✅ COMPLETED
```
server/services/image_generation/
├── __init__.py              # Exports GeminiImageService
└── gemini_service.py        # GeminiImageService class with:
                             #   - generate_image(prompt, reference_images) -> PIL Image
                             #   - generate_image_bytes(prompt, reference_images) -> bytes
                             #   - Configurable aspect_ratio ("16:9" default)
                             #   - Configurable resolution ("4K" default)
```

### Frontend
```
client/src/pages/images/
├── Images.tsx
├── components/
│   ├── UserSelector.tsx
│   ├── IdentitySelector.tsx
│   ├── ReferenceImageManager.tsx
│   ├── ReferenceImageSlot.tsx
│   └── GeneratedImageDisplay.tsx
└── hooks/
    ├── use-image-generation.ts
    └── use-reference-images.ts

client/src/api/
├── imageGeneration.ts
└── referenceImages.ts
```

## Notes

- **Reference Images are persistent**: Each user can have up to 5 reference images stored in S3. When you select a user, their stored reference images are loaded and displayed.
- **Reference Images belong to users**: When you select yourself vs a test user, you see/manage different sets of reference images.
- **Gemini API model**: `gemini-3-pro-image-preview` is used for text-and-image-to-image generation
- **S3 Storage**: All images (reference and generated) are stored in S3 via `default_storage`
- **Generated images can be saved to Identity**: After generation, you can save directly to the identity's `image` field using the existing endpoint
