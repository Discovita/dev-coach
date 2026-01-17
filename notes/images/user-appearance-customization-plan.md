# User Appearance Customization for Image Generation

## Overview

Add user appearance customization options to the Images page so users can describe how they want to visualize themselves (which may differ from their actual appearance). These options will be injected into the image generation prompt to create personalized identity images.

## Current State

### Frontend (Images Page)
- Location: `client/src/pages/images/Images.tsx`
- Components: UserSelector, IdentitySelector, ReferenceImageManager, GeneratedImageDisplay
- Has "Additional Prompt" textarea for extra instructions
- Calls backend via `useImageGeneration` hook

### Backend (Image Generation)
- Endpoint: `POST /api/v1/admin/identities/generate-image/`
- ViewSet: `AdminIdentityViewSet.generate_image()`
- Orchestration: `services/image_generation/orchestration.py`
- Prompt building: `PromptManager.create_image_generation_prompt()` → `get_identity_context_for_image()`

### Current Prompt Flow
1. Fetch latest active `IMAGE_GENERATION` prompt from database
2. Get identity context (name, category, I Am statement, visualization, notes)
3. Format with `{identity_context}` and `{additional_prompt}` placeholders
4. **No body/appearance description is currently included**

### Existing Enum Pattern
- Backend: Django `TextChoices` in `server/enums/`
- Frontend: TypeScript enums in `client/src/enums/`
- API: `CoreViewSet.enums()` at `/api/v1/core/enums`
- Frontend hook: `useCoreEnums()`

---

## Proposed Appearance Options

Based on the research scripts (`generate_generic_identity_image.py`), the following customization options are needed:

### 1. Gender
- **Options**: man, woman, person (gender neutral)
- **UI**: Badge selection (3 options)

### 2. Skin Tone (Apple Emoji Style)
Instead of ethnicity, use skin tone following Apple's emoji approach:
- **Options**: 
  - Light (🏻)
  - Medium-Light (🏼)
  - Medium (🏽)
  - Medium-Dark (🏾)
  - Dark (🏿)
- **UI**: Color swatch badges (5 options)
- **Note**: Uses visual representation rather than ethnic labels

### 3. Hair Color
- **Options**: black, brown, blonde, red, auburn, gray, white, bald
- **UI**: Color swatch badges with labels

### 4. Eye Color
- **Options**: brown, blue, green, hazel, gray, amber
- **UI**: Color swatch badges with labels

### 5. Height
- **Options**: short, below average, average, above average, tall
- **UI**: Badge selection

### 6. Build
- **Options**: slim, athletic, average, stocky, large
- **UI**: Badge selection

### 7. Age Range
- **Options**: young adult (20s), in their 30s, in their 40s, middle-aged (50s), mature (60+)
- **UI**: Badge selection

### 8. Hair Style (Optional)
- **Options**: short, medium, long, bald, curly, straight, wavy
- **UI**: Badge selection
- **Note**: Could be combined with hair color in natural language

---

## Architecture Decisions

### Decision 1: Appearance Settings → User Model ✅

User appearance settings (gender, skin tone, hair color, etc.) are stored on the **User Model**.

**Rationale:**
- Appearance is user-specific, not identity-specific
- Set once, applies to all identity image generations
- Persists across sessions
- User can update their preferences anytime

**UI Location:**
- **THIS IMPLEMENTATION:** Appearance selectors are on the **Images page** (admin tool)
- **FUTURE (production website):** Will be moved to a dedicated **Settings page**

**User Flow (This Implementation):**
1. User goes to Images page
2. Fills out appearance preferences (badge selectors) in the appearance section
3. Selections are saved to their User profile
4. When generating any identity image, these settings are pulled automatically

---

### Decision 2: Scene Questions → Identity Model ✅[]

Three scene-specific questions are stored on the **Identity Model**:

| Question | Field Name | Description |
|----------|------------|-------------|
| What are you wearing? | `clothing` | Outfit/attire for this identity visualization |
| How do you feel? | `mood` | Emotional state (proud, passionate, confident, etc.) |
| What is the setting? | `setting` | Environment/location for the scene |

**Rationale:**
- These vary per identity (a "Castle Builder" wears different clothes than a "Conductor")
- The mood/feeling is specific to each identity's visualization
- The setting/environment is completely different per identity
- Already have `visualization` field for free-form description; these are more structured inputs

**User Flow (on Images page):**
1. User selects an identity
2. If clothing/mood/setting are already set on the identity, they display pre-filled
3. User can edit these values for the image generation
4. Values are saved back to the identity for future use

**Note:** The existing `visualization` field remains as a free-form "vivid mental image" description. These three new fields provide structured, specific inputs that complement it.

---

---

## Data Model Summary

### User Model (New Fields for Appearance)
```python
# Appearance preferences - set via Images page (future: Settings page)
gender                    # man, woman, person
skin_tone                 # light, medium_light, medium, medium_dark, dark
hair_color                # black, brown, blonde, red, auburn, gray, white, bald
eye_color                 # brown, blue, green, hazel, gray, amber
height                    # short, below_average, average, above_average, tall
build                     # slim, athletic, average, stocky, large
age_range                 # twenties, thirties, forties, fifties, sixty_plus
```

### Identity Model (New Fields for Scene)
```python
# Scene-specific fields - varies per identity
clothing     # TextField: "linen button-down shirt", "formal conductor's attire"
mood         # TextField: "proud and calm", "passionate and focused"
setting      # TextField: "on a hill overlooking Hawaiian agricultural land", "grand concert hall"
```

---

## Implementation Plan

### Phase 1: Backend - Enums

#### 1.1 Create Appearance Enums
Create new enum files in `server/enums/`:

```
server/enums/
├── appearance/
│   ├── __init__.py
│   ├── gender.py
│   ├── skin_tone.py
│   ├── hair_color.py
│   ├── eye_color.py
│   ├── height.py
│   ├── build.py
│   └── age_range.py
```

Each enum follows the existing pattern:

```python
# server/enums/appearance/gender.py
from django.db import models

class Gender(models.TextChoices):
    MAN = "man", "Man"
    WOMAN = "woman", "Woman"
    PERSON = "person", "Person"  # Gender neutral
```

```python
# server/enums/appearance/skin_tone.py
from django.db import models

class SkinTone(models.TextChoices):
    """
    Skin tone options following Apple emoji convention.
    """
    LIGHT = "light", "Light"
    MEDIUM_LIGHT = "medium_light", "Medium-Light"
    MEDIUM = "medium", "Medium"
    MEDIUM_DARK = "medium_dark", "Medium-Dark"
    DARK = "dark", "Dark"
```

#### 1.2 Update CoreViewSet to Serve Appearance Enums

```python
# server/apps/core/views.py
@decorators.action(detail=False, methods=["get"], url_path="enums")
def enums(self, request, *args, **kwargs):
    # ... existing enums ...
    
    # Appearance enums
    genders = [{"value": g.value, "label": g.label} for g in Gender]
    skin_tones = [{"value": s.value, "label": s.label} for s in SkinTone]
    hair_colors = [{"value": h.value, "label": h.label} for h in HairColor]
    eye_colors = [{"value": e.value, "label": e.label} for e in EyeColor]
    heights = [{"value": h.value, "label": h.label} for h in Height]
    builds = [{"value": b.value, "label": b.label} for b in Build]
    age_ranges = [{"value": a.value, "label": a.label} for a in AgeRange]
    
    return Response({
        # ... existing ...
        "appearance": {
            "genders": genders,
            "skin_tones": skin_tones,
            "hair_colors": hair_colors,
            "eye_colors": eye_colors,
            "heights": heights,
            "builds": builds,
            "age_ranges": age_ranges,
        }
    })
```

---

### Phase 2: Backend - User Model

#### 2.1 Add Appearance Fields to User Model

```python
# server/apps/users/models/user.py (add fields)

# Appearance/visualization preferences for image generation
gender = models.CharField(
    max_length=20,
    choices=Gender.choices,
    null=True,
    blank=True,
    help_text="Gender preference for image generation"
)
skin_tone = models.CharField(
    max_length=20,
    choices=SkinTone.choices,
    null=True,
    blank=True,
    help_text="Preferred skin tone for image generation"
)
hair_color = models.CharField(
    max_length=20,
    choices=HairColor.choices,
    null=True,
    blank=True,
    help_text="Preferred hair color for image generation"
)
eye_color = models.CharField(
    max_length=20,
    choices=EyeColor.choices,
    null=True,
    blank=True,
    help_text="Preferred eye color for image generation"
)
height = models.CharField(
    max_length=20,
    choices=Height.choices,
    null=True,
    blank=True,
    help_text="Height preference for image generation"
)
build = models.CharField(
    max_length=20,
    choices=Build.choices,
    null=True,
    blank=True,
    help_text="Build/body type preference for image generation"
)
age_range = models.CharField(
    max_length=20,
    choices=AgeRange.choices,
    null=True,
    blank=True,
    help_text="Age range preference for image generation"
)
```

#### 2.2 Create Migration
```bash
python manage.py makemigrations users --name add_appearance_fields
python manage.py migrate
```

#### 2.3 Update User Serializers
Add appearance fields to:
- `UserSerializer`
- `UserProfileSerializer`

---

### Phase 3: Backend - Identity Model (Scene Fields)

#### 3.1 Add Scene Fields to Identity Model

```python
# server/apps/identities/models.py (add fields)

clothing = models.TextField(
    null=True,
    blank=True,
    help_text="What the person is wearing in this identity visualization (e.g., 'linen button-down shirt')"
)
mood = models.TextField(
    null=True,
    blank=True,
    help_text="Emotional state/feeling in this identity visualization (e.g., 'proud and calm')"
)
setting = models.TextField(
    null=True,
    blank=True,
    help_text="Environment/location for this identity visualization (e.g., 'on a hill overlooking the ocean')"
)
```

#### 3.2 Create Migration
```bash
python manage.py makemigrations identities --name add_scene_fields
python manage.py migrate
```

#### 3.3 Update Identity Serializer
Add the three new fields to `IdentitySerializer` in `server/apps/identities/serializer.py`.

---

### Phase 4: Backend - Prompt Integration

#### 4.1 Create Appearance Context Builder

```python
# server/services/prompt_manager/utils/context/func/get_appearance_context.py
"""
Build body/appearance description from user preferences.
"""
from apps.users.models import User
from services.logger import configure_logging

log = configure_logging(__name__)

def get_appearance_context(user: User) -> str:
    """
    Build a natural language body description from user appearance preferences.
    
    Returns:
        String like "a tall athletic man with medium skin tone, brown hair, and blue eyes in their 30s"
    """
    parts = []
    
    # Height
    if user.height:
        parts.append(user.height.replace("_", " "))
    
    # Build
    if user.build:
        parts.append(user.build.replace("_", " "))
    
    # Skin tone
    if user.skin_tone:
        parts.append(f"{user.skin_tone.replace('_', '-')}-skinned")
    
    # Gender
    if user.gender:
        parts.append(user.gender)
    
    # Age
    if user.age_range:
        parts.append(user.age_range.replace("_", " "))
    
    # Hair and eyes
    hair_eye_parts = []
    if user.hair_color:
        hair_eye_parts.append(f"{user.hair_color} hair")
    if user.eye_color:
        hair_eye_parts.append(f"{user.eye_color} eyes")
    
    if hair_eye_parts:
        parts.append(f"with {' and '.join(hair_eye_parts)}")
    
    if not parts:
        return ""
    
    return "a " + " ".join(parts)
```

#### 4.2 Create Scene Context Builder

```python
# server/services/prompt_manager/utils/context/func/get_scene_context.py
"""
Build scene description from identity fields.
"""
from apps.identities.models import Identity
from services.logger import configure_logging

log = configure_logging(__name__)

def get_scene_context(identity: Identity) -> str:
    """
    Build scene description from identity's clothing, mood, and setting fields.
    
    Returns:
        String describing the scene elements, or empty string if none set.
    """
    parts = []
    
    if identity.clothing:
        parts.append(f"CLOTHING: {identity.clothing}")
    
    if identity.mood:
        parts.append(f"MOOD/FEELING: {identity.mood}")
    
    if identity.setting:
        parts.append(f"SETTING: {identity.setting}")
    
    if not parts:
        return ""
    
    return "\n".join(parts)
```

#### 4.3 Update Image Generation Orchestration

```python
# server/services/image_generation/orchestration.py
def generate_identity_image(
    identity: Identity,
    reference_images: List[ReferenceImage],
    user: User,  # NEW: pass user for appearance context
    additional_prompt: str = "",
    aspect_ratio: str = "16:9",
    resolution: str = "4K",
) -> Optional[PILImage.Image]:
```

#### 4.4 Update PromptManager

```python
# server/services/prompt_manager/manager.py
def create_image_generation_prompt(
    self,
    identity: Identity,
    user: User,  # NEW: for appearance context
    additional_prompt: str = "",
) -> str:
    from services.prompt_manager.utils.context.func import (
        get_identity_context_for_image,
        get_appearance_context,  # NEW
        get_scene_context,       # NEW
    )
    
    identity_context = get_identity_context_for_image(identity)
    appearance_context = get_appearance_context(user)   # NEW: from User model
    scene_context = get_scene_context(identity)         # NEW: from Identity model
    
    formatted_prompt = prompt.body.format(
        identity_context=identity_context,
        appearance_context=appearance_context,  # NEW placeholder
        scene_context=scene_context,            # NEW placeholder
        additional_prompt=additional_prompt or "None provided",
    )
```

#### 4.5 Update Image Generation Prompt in Database
Add placeholders to the IMAGE_GENERATION prompt template:
- `{appearance_context}` - User's appearance preferences
- `{scene_context}` - Identity's clothing, mood, setting

---

### Phase 5: Backend - API Updates

#### 5.1 Update AdminIdentityViewSet.generate_image

```python
def generate_image(self, request):
    # ... existing code ...
    
    # Fetch user for appearance context
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(...)
    
    # Generate with user appearance
    pil_image = generate_identity_image(
        identity=identity,
        reference_images=reference_images,
        user=target_user,  # NEW
        additional_prompt=additional_prompt,
    )
```

#### 5.2 Add Endpoint to Update User Appearance
Could be part of existing user update endpoint or a dedicated endpoint:

```
PATCH /api/v1/user/me/appearance
{
    "gender": "man",
    "skin_tone": "medium",
    "hair_color": "brown",
    ...
}
```

#### 5.3 Identity Scene Fields
The existing Identity endpoints already support update. The Identity serializer just needs to include the three new fields (clothing, mood, setting) and they'll be updatable via:

```
PATCH /api/v1/identities/{id}
{
    "clothing": "linen button-down shirt",
    "mood": "proud and calm",
    "setting": "on a hill overlooking Hawaiian agricultural land"
}
```

---

### Phase 6: Frontend - Enums

#### 6.1 Create TypeScript Enums

```
client/src/enums/
├── appearance/
│   ├── gender.ts
│   ├── skinTone.ts
│   ├── hairColor.ts
│   ├── eyeColor.ts
│   ├── height.ts
│   ├── build.ts
│   └── ageRange.ts
```

Example:
```typescript
// client/src/enums/appearance/skinTone.ts
export enum SkinTone {
  LIGHT = "light",
  MEDIUM_LIGHT = "medium_light",
  MEDIUM = "medium",
  MEDIUM_DARK = "medium_dark",
  DARK = "dark",
}

export const SKIN_TONE_DISPLAY: Record<SkinTone, { label: string; color: string }> = {
  [SkinTone.LIGHT]: { label: "Light", color: "#ffecd2" },
  [SkinTone.MEDIUM_LIGHT]: { label: "Medium-Light", color: "#e8c4a2" },
  [SkinTone.MEDIUM]: { label: "Medium", color: "#c49a6c" },
  [SkinTone.MEDIUM_DARK]: { label: "Medium-Dark", color: "#8d5524" },
  [SkinTone.DARK]: { label: "Dark", color: "#5c3836" },
};
```

#### 6.2 Update useCoreEnums Hook
Add types for appearance enums in the response.

---

### Phase 7: Frontend - UI Components

#### 7.1 Create AppearanceSelector Component (User Appearance)

```
client/src/pages/images/components/
├── AppearanceSelector.tsx        # Main container for user appearance
├── appearance/
│   ├── GenderSelector.tsx
│   ├── SkinToneSelector.tsx
│   ├── HairColorSelector.tsx
│   ├── EyeColorSelector.tsx
│   ├── HeightSelector.tsx
│   ├── BuildSelector.tsx
│   └── AgeRangeSelector.tsx
```

#### 7.2 Create SceneInputs Component (Identity Scene)

```
client/src/pages/images/components/
├── SceneInputs.tsx               # Container for scene fields
├── scene/
│   ├── ClothingInput.tsx         # "What are you wearing?"
│   ├── MoodInput.tsx             # "How do you feel?"
│   └── SettingInput.tsx          # "What is the setting?"
```

These are text inputs (not badge selectors) since the values are free-form text.

#### 7.3 Badge Selection UI Pattern

```tsx
// Generic badge selector component
interface BadgeSelectorProps {
  label: string;
  options: Array<{ value: string; label: string; color?: string }>;
  value: string | null;
  onChange: (value: string) => void;
}

function BadgeSelector({ label, options, value, onChange }: BadgeSelectorProps) {
  return (
    <div className="space-y-2">
      <label className="text-sm font-medium">{label}</label>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => onChange(option.value)}
            className={cn(
              "px-3 py-1.5 rounded-full text-sm font-medium transition-all",
              "border-2",
              value === option.value
                ? "border-primary bg-primary text-primary-foreground"
                : "border-muted bg-background hover:border-primary/50"
            )}
            style={option.color ? { backgroundColor: value === option.value ? option.color : undefined } : undefined}
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  );
}
```

#### 7.4 Skin Tone Selector (Special Case)

```tsx
// Visual color swatches for skin tone
function SkinToneSelector({ value, onChange }: SelectorProps) {
  const tones = [
    { value: "light", color: "#ffecd2" },
    { value: "medium_light", color: "#e8c4a2" },
    { value: "medium", color: "#c49a6c" },
    { value: "medium_dark", color: "#8d5524" },
    { value: "dark", color: "#5c3836" },
  ];

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium">Skin Tone</label>
      <div className="flex gap-3">
        {tones.map((tone) => (
          <button
            key={tone.value}
            type="button"
            onClick={() => onChange(tone.value)}
            className={cn(
              "w-10 h-10 rounded-full transition-all",
              "border-2",
              value === tone.value
                ? "border-primary ring-2 ring-primary ring-offset-2"
                : "border-transparent hover:border-muted-foreground/30"
            )}
            style={{ backgroundColor: tone.color }}
            title={tone.value.replace("_", " ")}
          />
        ))}
      </div>
    </div>
  );
}
```

#### 7.5 Update Images.tsx

```tsx
// client/src/pages/images/Images.tsx
export default function Images() {
  // ... existing state ...
  
  // Appearance state (initially loaded from user profile)
  const [appearance, setAppearance] = useState<UserAppearance | null>(null);
  
  // Scene state (loaded from selected identity, can be edited)
  const [sceneInputs, setSceneInputs] = useState<SceneInputs>({
    clothing: "",
    mood: "",
    setting: "",
  });
  
  return (
    <div className="flex flex-col h-full w-full p-6 overflow-y-auto">
      <h1 className="text-3xl font-bold mb-6">Identity Image Generation</h1>

      <div className="mb-6">
        <UserSelector ... />
      </div>

      {selectedUserId && (
        <div className="flex-1 min-h-0 space-y-8">
          <ReferenceImageManager userId={selectedUserId} />

          {/* NEW: Appearance Selection Section (from User model) */}
          <AppearanceSelector 
            userId={selectedUserId}
            appearance={appearance}
            onAppearanceChange={setAppearance}
          />

          <div className="space-y-4">
            <IdentitySelector ... />
            
            {selectedIdentityId && (
              <>
                {/* NEW: Scene Inputs Section (from/to Identity model) */}
                <SceneInputs
                  identity={selectedIdentity}
                  values={sceneInputs}
                  onChange={setSceneInputs}
                />
                
                {/* ... rest of existing UI (additional prompt, generate button) ... */}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
```

---

### Phase 8: Frontend - API & Hooks

#### 8.1 Add API Functions

```typescript
// client/src/api/userAppearance.ts
export async function getUserAppearance(userId: string): Promise<UserAppearance> {
  const response = await authFetch(`${COACH_BASE_URL}/user/${userId}/appearance`);
  return response.json();
}

export async function updateUserAppearance(
  userId: string, 
  appearance: Partial<UserAppearance>
): Promise<UserAppearance> {
  const response = await authFetch(`${COACH_BASE_URL}/user/${userId}/appearance`, {
    method: "PATCH",
    body: JSON.stringify(appearance),
  });
  return response.json();
}
```

#### 8.2 Create useUserAppearance Hook

```typescript
// client/src/hooks/use-user-appearance.ts
export function useUserAppearance(userId: string) {
  const queryClient = useQueryClient();
  
  const query = useQuery({
    queryKey: ["user", userId, "appearance"],
    queryFn: () => getUserAppearance(userId),
    enabled: !!userId,
  });
  
  const mutation = useMutation({
    mutationFn: (appearance: Partial<UserAppearance>) => 
      updateUserAppearance(userId, appearance),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user", userId, "appearance"] });
    },
  });
  
  return {
    appearance: query.data,
    isLoading: query.isLoading,
    updateAppearance: mutation.mutateAsync,
    isUpdating: mutation.isPending,
  };
}
```

#### 8.3 Update useIdentities Hook (or use existing)

The existing `useIdentities` hook already supports updating identities. When saving scene inputs, we update the identity with the new clothing/mood/setting values:

```typescript
// When generating image, save scene inputs back to identity
await updateIdentity({
  id: selectedIdentityId,
  clothing: sceneInputs.clothing,
  mood: sceneInputs.mood,
  setting: sceneInputs.setting,
});
```

---

## File Changes Summary

### Backend Files to Create
```
server/enums/appearance/
├── __init__.py
├── gender.py
├── skin_tone.py
├── hair_color.py
├── eye_color.py
├── height.py
├── build.py
└── age_range.py

server/services/prompt_manager/utils/context/func/
├── get_appearance_context.py    # Build appearance from User model
└── get_scene_context.py         # Build scene from Identity model
```

### Backend Files to Modify
```
server/enums/__init__.py                           # Export new enums
server/apps/core/views.py                          # Add appearance enums to /enums endpoint
server/apps/users/models/user.py                   # Add 7 appearance fields
server/apps/users/serializers/user_serializer.py   # Add appearance fields
server/apps/users/serializers/user_profile_serializer.py
server/apps/users/admin.py                         # Add appearance fieldset
server/apps/users/views/user_viewset.py            # Add appearance update endpoint
server/apps/identities/models.py                   # Add 3 scene fields (clothing, mood, setting)
server/apps/identities/serializer.py               # Add scene fields
server/apps/identities/admin.py                    # Add scene fields to admin
server/services/image_generation/orchestration.py  # Pass user for appearance
server/services/prompt_manager/manager.py          # Add appearance + scene to prompt
server/apps/identities/views/admin_identity_view_set.py  # Pass user to orchestration
```

### Frontend Files to Create
```
client/src/enums/appearance/
├── index.ts
├── gender.ts
├── skinTone.ts
├── hairColor.ts
├── eyeColor.ts
├── height.ts
├── build.ts
└── ageRange.ts

client/src/types/userAppearance.ts
client/src/types/sceneInputs.ts

client/src/api/userAppearance.ts

client/src/hooks/use-user-appearance.ts

client/src/pages/images/components/
├── AppearanceSelector.tsx          # Container for user appearance badges
├── SceneInputs.tsx                 # Container for scene text inputs
├── appearance/
│   ├── BadgeSelector.tsx
│   ├── GenderSelector.tsx
│   ├── SkinToneSelector.tsx
│   ├── HairColorSelector.tsx
│   ├── EyeColorSelector.tsx
│   ├── HeightSelector.tsx
│   ├── BuildSelector.tsx
│   └── AgeRangeSelector.tsx
└── scene/
    ├── ClothingInput.tsx           # "What are you wearing?"
    ├── MoodInput.tsx               # "How do you feel?"
    └── SettingInput.tsx            # "What is the setting?"
```

### Frontend Files to Modify
```
client/src/pages/images/Images.tsx                 # Add AppearanceSelector + SceneInputs
client/src/types/user.ts                           # Add appearance fields
client/src/types/identity.ts                       # Add scene fields
client/src/hooks/use-core.ts                       # Update types for appearance enums
```

### Database Migrations
```
users/migrations/XXXX_add_appearance_fields.py     # 7 new User fields
identities/migrations/XXXX_add_scene_fields.py     # 3 new Identity fields
```

### Prompts (Database)
```
Update IMAGE_GENERATION prompt to include:
- {appearance_context} placeholder (from User)
- {scene_context} placeholder (from Identity)
```

---

## UI Mockup

```
┌─────────────────────────────────────────────────────────────────────┐
│  Identity Image Generation                                          │
├─────────────────────────────────────────────────────────────────────┤
│  [User Selector ▼]                                                  │
├─────────────────────────────────────────────────────────────────────┤
│  Reference Images (up to 5)                                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │   📷    │ │   📷    │ │   +     │ │   +     │ │   +     │       │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘       │
├─────────────────────────────────────────────────────────────────────┤
│  How would you like to visualize yourself?                          │
│  ⓘ These settings are saved to your user profile                    │
│                                                                     │
│  Gender                                                             │
│  [Man] [Woman] [Person]                                             │
│                                                                     │
│  Skin Tone                                                          │
│  ⚪ ⚪ ⚪ ⚪ ⚪  (color swatches from light to dark)                 │
│                                                                     │
│  Hair Color                                                         │
│  [Black] [Brown] [Blonde] [Red] [Auburn] [Gray] [White] [Bald]     │
│                                                                     │
│  Eye Color                                                          │
│  [Brown] [Blue] [Green] [Hazel] [Gray] [Amber]                     │
│                                                                     │
│  Height                                                             │
│  [Short] [Below Average] [Average] [Above Average] [Tall]          │
│                                                                     │
│  Build                                                              │
│  [Slim] [Athletic] [Average] [Stocky] [Large]                      │
│                                                                     │
│  Age                                                                │
│  [20s] [30s] [40s] [50s] [60+]                                     │
├─────────────────────────────────────────────────────────────────────┤
│  Select Identity                                                    │
│  [Identity Selector ▼]                                              │
│                                                                     │
│  Identity: "Castle Builder"  Category: Romantic Relation            │
├─────────────────────────────────────────────────────────────────────┤
│  Scene Details for this Identity                                    │
│  ⓘ These are saved to the identity                                  │
│                                                                     │
│  What are you wearing?                                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ linen button-down shirt                                     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  How do you feel?                                                   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ proud and calm                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  What is the setting?                                               │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ on a hill overlooking Hawaiian agricultural land with       │   │
│  │ view of the ocean                                           │   │
│  └─────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────┤
│  Additional Prompt (Optional)                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                                                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  [✨ Generate Image]                                                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Progress

> **Status:** In Progress | **Last Updated:** 2026-01-17

### Phase 1-2: Backend Enums & API ✅
- [x] 1. Create appearance enums (`server/enums/appearance/`)
  - [x] `gender.py`
  - [x] `skin_tone.py`
  - [x] `hair_color.py`
  - [x] `eye_color.py`
  - [x] `height.py`
  - [x] `build.py`
  - [x] `age_range.py`
  - [x] `__init__.py` (exports)
- [x] 2. Update CoreViewSet to serve appearance enums

**📚 Phase 1-2 Documentation:**
- [x] Update `docs/docs/api/endpoints/core.md` - Add appearance enums to `/enums` endpoint docs

---

### Phase 3: Backend - Identity Model ✅
- [x] 3. Add scene fields to Identity model (`clothing`, `mood`, `setting`)
- [x] 4. Create Identity migration by running the command: `python manage.py makemigrations identities --name add_scene_fields`
- [x] 5. Update Identity serializer
- [x] 6. Update Identity admin

**📚 Phase 3 Documentation:**
- [x] Update `docs/docs/database/models/identity.md` - Add clothing, mood, setting fields
- [x] Update `docs/docs/api/endpoints/identities.md` - Add scene fields to request/response docs

---

### Phase 4: Backend - User Model ✅
- [x] 7. Add appearance fields to User model (7 fields)
- [x] 8. Create User migration
- [x] 9. Update User serializers (`UserSerializer`, `UserProfileSerializer`)
- [x] 10. Update User admin

**📚 Phase 4 Documentation:**
- [x] Update `docs/docs/database/models/users.md` - Add 7 appearance fields
- [x] Update `docs/docs/api/endpoints/users.md` - Add appearance fields to request/response docs

---

### Phase 5: Backend - Prompt Integration ✅
- [x] 11. Create `get_appearance_context()` function
- [x] 12. Create `get_scene_context()` function
- [x] 13. Update `PromptManager.create_image_generation_prompt()` to include both contexts
- [x] 14. Update `orchestration.generate_identity_image()` to pass user
- [x] 15. Update `AdminIdentityViewSet.generate_image()` to pass user to orchestration

**📚 Phase 5 Documentation:**
- [x] Create `docs/docs/core-systems/prompt-manager/context-keys/appearance-context.md`
- [x] Create `docs/docs/core-systems/prompt-manager/context-keys/scene-context.md`
- [x] Update `docs/docs/core-systems/prompt-manager/context-keys/overview.md` - Add new context keys
- [x] Update `sidebars.ts` - Add new context key docs to sidebar

---

### Phase 6: Frontend - Types & Enums ✅
- [x] 16. Create TypeScript appearance enums (`client/src/enums/appearance/`)
  - [x] `gender.ts`
  - [x] `skinTone.ts`
  - [x] `hairColor.ts`
  - [x] `eyeColor.ts`
  - [x] `height.ts`
  - [x] `build.ts`
  - [x] `ageRange.ts`
  - [x] `index.ts` (exports)
- [x] 17. Add `UserAppearance` type (`client/src/types/userAppearance.ts`)
- [x] 18. Add `SceneInputs` type (`client/src/types/sceneInputs.ts`)
- [x] 19. Update `Identity` type with scene fields (`clothing`, `mood`, `setting`)
- [x] 20. Update `User` type with appearance fields (7 fields)
- [x] 21. Create `CoreEnumsResponse` type for API response
- [x] 22. Update `useCoreEnums` hook with proper types

**📚 Phase 6 Documentation:**
- [x] Create `docs/docs/frontend/types/user-appearance.md`
- [x] Create `docs/docs/frontend/types/scene-inputs.md`
- [x] Update `sidebars.ts` - Add new type docs to sidebar

---

### Phase 7: Frontend - UI Components ✅
- [x] 21. Create `BadgeSelector` reusable component
- [x] 22. Create `AppearanceSelector` container component
- [x] 23. Create individual appearance selectors (Gender, SkinTone, Hair, etc.)
- [x] 24. Create `SceneInputs` component (3 text inputs)

**📚 Phase 7 Documentation:**
- [x] (No docs needed - internal components)

---

### Phase 8: Frontend - API & Integration ✅
- [x] 25. Add API functions for user appearance
- [x] 26. Create `useUserAppearance` hook
- [x] 27. Update `Images.tsx` to include `AppearanceSelector`
- [x] 28. Update `Images.tsx` to include `SceneInputs`
- [x] 29. Wire up save/load for appearance data
- [x] 30. Wire up save/load for scene data (to Identity)

**📚 Phase 8 Documentation:**
- [x] (No docs needed - frontend implementation details)

---

### Phase 9: Database & Prompt 🔄
- [x] 31. Apply all migrations (requires manual execution with Docker access)
  - ```sh
  COMPOSE_PROJECT_NAME=dev-coach-local \
    docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml exec backend python manage.py migrate
  ```
- [x] 32. Update IMAGE_GENERATION prompt with `{appearance_context}` placeholder
- [x] 33. Update IMAGE_GENERATION prompt with `{scene_context}` placeholder

**📚 Phase 9 Documentation:**
- [x] Update `docs/docs/database/schema/overview.md` - Reflect schema changes (if applicable)

---

### Phase 10: Appearance Selection UX Improvements ⬜

**Goal:** Improve the appearance selection UX to show current selections, require all fields, and provide explicit save functionality.

#### Requirements:
1. **Display Current Selections:** Show visual indication of which options are currently selected
2. **Save Button:** Add explicit save button to persist selections to user model
3. **Validation:** Show message if not all fields are selected (all 7 are required for image generation)
4. **Load Saved Values:** When navigating to page/selecting user, load their saved appearance preferences
5. **Admin Context:** Handle both current user and test accounts (admin viewing another user's settings)

#### Current Behavior Analysis:
- `AppearanceSelector` receives `appearance` prop from `useUserAppearance` hook
- `useUserAppearance` already fetches appearance on mount and provides `updateAppearance` mutation
- Currently, `handleAppearanceChange` in `Images.tsx` calls `updateAppearance` on every change (auto-save)
- Selections are visually indicated via `value` prop passed to each selector

#### Issues to Address:
1. Auto-save on every click is not ideal UX - user may want to review before saving
2. No clear indication of which fields are missing
3. No explicit save button - user doesn't know when changes are saved
4. No validation message about required fields

#### Implementation Tasks:

**10.1 Update AppearanceSelector Component**
- [x] Add local state to track unsaved changes
- [x] Add "Save Preferences" button at bottom of section
- [x] Add validation to check if all 7 fields are selected
- [x] Show warning message if any fields are missing
- [x] Show "saved" indicator or success state after save
- [x] Show which fields are currently selected vs. missing

**10.2 Update Images.tsx**
- [x] Change from auto-save to manual save pattern
- [x] Track dirty state for appearance changes
- [x] Pass save handler to AppearanceSelector

**10.3 Visual Indicators**
- [x] Add checkmark or highlight to show selected options
- [x] Add visual indicator for missing/required fields
- [x] Add loading state during save operation
- [x] Add success toast on save

**10.4 Validation Logic**
- [x] Create helper to check if all appearance fields are filled
- [x] Show inline validation messages for missing fields
- [ ] Optionally disable image generation if appearance incomplete

#### Files to Modify:
```
client/src/pages/images/components/appearance/AppearanceSelector.tsx
client/src/pages/images/Images.tsx
```

#### UI Mockup (Updated AppearanceSelector):
```
┌─────────────────────────────────────────────────────────────────────┐
│  How would you like to visualize yourself?                          │
│  ⓘ These settings are saved to your user profile                    │
│                                                                     │
│  ⚠️ Please select all options to enable image generation            │
│                                                                     │
│  Gender ✓                                                           │
│  [Man] [Woman] [Person]                                             │
│                                                                     │
│  Skin Tone ✓                                                        │
│  ⚪ ⚪ ⚪ ⚪ ⚪                                                        │
│                                                                     │
│  Hair Color ✗ (required)                                            │
│  [Black] [Brown] [Blonde] [Red] [Auburn] [Gray] [White] [Bald]     │
│                                                                     │
│  Eye Color ✓                                                        │
│  [Brown] [Blue] [Green] [Hazel] [Gray] [Amber]                     │
│                                                                     │
│  Height ✗ (required)                                                │
│  [Short] [Below Average] [Average] [Above Average] [Tall]          │
│                                                                     │
│  Build ✓                                                            │
│  [Slim] [Athletic] [Average] [Stocky] [Large]                      │
│                                                                     │
│  Age ✓                                                              │
│  [20s] [30s] [40s] [50s] [60+]                                     │
│                                                                     │
│  [💾 Save Preferences]  ← Disabled until all fields selected        │
│                                                                     │
│  5 of 7 fields selected                                             │
└─────────────────────────────────────────────────────────────────────┘
```

#### Acceptance Criteria:
- [x] User can see which appearance options are currently selected
- [x] User can see which fields are missing (validation)
- [x] User must select all 7 fields before saving (validation warning shown, but save still allowed)
- [x] Save button persists selections to user model
- [x] When navigating to page, saved selections are loaded and displayed
- [x] Works for both current user (self) and test accounts (admin viewing)
- [x] Success feedback shown after saving

---

### Phase 11: Scene Details Save Functionality ⬜

#### Overview

Currently, the Scene Details section (`SceneInputs` component) displays three text inputs (clothing, mood, setting) that are loaded from the selected identity. However, there is no explicit "Save" button - the data is only saved when the user clicks "Generate Image". This phase adds:

1. A dedicated "Save Scene Details" button to the `SceneInputs` component
2. Dirty state tracking (detect unsaved changes)
3. Disable image generation until scene details are saved
4. Auto-populate inputs when switching identities (already works)
5. Success/error feedback on save

#### Current Behavior

- Scene inputs are loaded from identity when selected ✅
- Scene inputs are saved to identity **only when Generate Image is clicked** ❌
- No visual indication of unsaved changes ❌
- Can generate image without explicitly saving scene details ❌

#### Desired Behavior

- Scene inputs are loaded from identity when selected ✅
- Scene inputs can be saved independently via "Save Scene Details" button ✅
- Visual indication when there are unsaved changes ✅
- Cannot generate image until scene details are saved ✅
- Success feedback after saving ✅

#### Implementation Tasks

##### 11.1 Update `SceneInputs` Component ⬜

**File:** `client/src/pages/images/components/SceneInputs.tsx`

**Changes:**
1. Add props for:
   - `savedValues: SceneInputsType` - the values currently saved on the identity
   - `onSave: () => Promise<void>` - callback to save changes
   - `isSaving: boolean` - loading state
   - `disabled?: boolean` - disable inputs when no identity selected

2. Add local state tracking:
   - `isDirty` - computed by comparing `values` to `savedValues`
   - `showSaveSuccess` - temporary success indicator

3. Add footer section (similar to `AppearanceSelector`):
   - Progress/status indicator (e.g., "Unsaved changes" or "All changes saved")
   - "Save Scene Details" button
   - Success indicator after save

4. Style the component to match `AppearanceSelector` pattern

**Reference Pattern:** `AppearanceSelector.tsx` lines 103-272

##### 11.2 Update `Images.tsx` to Support Scene Save ⬜

**File:** `client/src/pages/images/Images.tsx`

**Changes:**

1. Track saved scene values separately from local edits:
   ```typescript
   // Current local values (for editing)
   const [sceneInputs, setSceneInputs] = useState<SceneInputsType>({...});
   
   // Track if scene has been saved (for enabling generate button)
   const [sceneSaved, setSceneSaved] = useState(false);
   ```

2. Add `handleSceneSave` function:
   - Calls `updateIdentity()` with scene fields
   - Invalidates identity queries
   - Sets `sceneSaved = true`
   - Shows toast on success/error

3. Update `useEffect` that loads scene inputs:
   - When identity changes, load values AND set `sceneSaved = true` (if values exist) or `false` (if empty)

4. Update `canGenerate` logic:
   - Add condition: scene must be saved OR scene inputs must match saved values

5. Remove scene save from `handleGenerate`:
   - Currently `saveSceneInputsToIdentity()` is called before generating
   - This should be removed - user must explicitly save first

6. Pass new props to `SceneInputs`:
   ```tsx
   <SceneInputs
     values={sceneInputs}
     savedValues={selectedIdentity ? {
       clothing: selectedIdentity.clothing || "",
       mood: selectedIdentity.mood || "",
       setting: selectedIdentity.setting || "",
     } : { clothing: "", mood: "", setting: "" }}
     onChange={setSceneInputs}
     onSave={handleSceneSave}
     isSaving={isSavingScene}
     disabled={!selectedIdentityId}
   />
   ```

##### 11.3 Add Save Loading State ⬜

**File:** `client/src/pages/images/Images.tsx`

**Changes:**
1. Add `isSavingScene` state to track save operation
2. Set to `true` when save starts, `false` when complete

##### 11.4 Update Generate Button Disabled State ⬜

**File:** `client/src/pages/images/Images.tsx`

**Changes:**
1. Update `canGenerate` to require scene details to be saved:
   ```typescript
   const sceneIsDirty = selectedIdentity && (
     sceneInputs.clothing !== (selectedIdentity.clothing || "") ||
     sceneInputs.mood !== (selectedIdentity.mood || "") ||
     sceneInputs.setting !== (selectedIdentity.setting || "")
   );
   
   const canGenerate =
     selectedUserId &&
     selectedIdentityId &&
     hasReferenceImages &&
     !isGenerating &&
     !sceneIsDirty; // NEW: Must save scene details first
   ```

2. Add helper text below Generate button when disabled due to unsaved scene:
   ```tsx
   {sceneIsDirty && (
     <p className="text-sm text-amber-600">
       Save scene details before generating an image.
     </p>
   )}
   ```

##### 11.5 Add Validation Warning to SceneInputs ⬜

**File:** `client/src/pages/images/components/SceneInputs.tsx`

**Changes:**
1. Add optional validation warning when fields are empty:
   ```tsx
   {!hasAllFields && (
     <div className="flex items-start gap-2 p-3 bg-amber-50 ...">
       <AlertCircle className="size-4 text-amber-600" />
       <div className="text-sm text-amber-800">
         <p className="font-medium">Fill in all scene details for best results</p>
         <p className="text-xs mt-1">Missing: {missingFields.join(", ")}</p>
       </div>
     </div>
   )}
   ```

2. Note: This is a soft warning, not a hard requirement - user can still save with empty fields

#### Task Checklist

| # | Task | File | Status |
|---|------|------|--------|
| 11.1 | Update SceneInputs with save button and dirty tracking | `SceneInputs.tsx` | ⬜ |
| 11.2 | Update Images.tsx with handleSceneSave and new props | `Images.tsx` | ⬜ |
| 11.3 | Add isSavingScene loading state | `Images.tsx` | ⬜ |
| 11.4 | Update canGenerate to require saved scene | `Images.tsx` | ⬜ |
| 11.5 | Add validation warning for empty fields | `SceneInputs.tsx` | ⬜ |

#### Acceptance Criteria

- [ ] When an identity is selected, scene details are auto-populated from the identity
- [ ] Changes to scene inputs show "Unsaved changes" indicator
- [ ] "Save Scene Details" button is enabled only when there are unsaved changes
- [ ] Clicking "Save Scene Details" saves to the identity and shows success feedback
- [ ] "Generate Image" button is disabled when scene details have unsaved changes
- [ ] Helper text explains why Generate is disabled (if due to unsaved scene)
- [ ] When switching identities, scene details are loaded from the new identity
- [ ] Empty fields show a soft warning but don't block saving

#### Files to Modify

1. `client/src/pages/images/components/SceneInputs.tsx` - Add save button, dirty tracking, validation
2. `client/src/pages/images/Images.tsx` - Add save handler, update canGenerate logic

#### No Documentation Updates Required

This is a frontend UX improvement - no API changes or new features that require documentation.

---

### Testing & Verification ⬜
- [ ] 34. Test appearance badge selection saves to user
- [ ] 35. Test scene inputs save to identity
- [ ] 36. Test image generation includes appearance in prompt
- [ ] 37. Test image generation includes scene details in prompt
- [ ] 38. End-to-end test: full flow generates correct image

**📚 Testing Documentation:**
- [ ] (No docs needed - testing is internal)

---

### Progress Summary

| Phase | Description | Code | Docs | Status |
|-------|-------------|------|------|--------|
| 1-2 | Backend Enums & API | ✅ | ✅ | ✅ Complete |
| 3 | Identity Model (scene fields) | ✅ | ✅ | ✅ Complete |
| 4 | User Model (appearance fields) | ✅ | ✅ | ✅ Complete |
| 5 | Prompt Integration | ✅ | ✅ | ✅ Complete |
| 6 | Frontend Types & Enums | ✅ | ✅ | ✅ Complete |
| 7 | Frontend UI Components | ✅ | — | ✅ Complete |
| 8 | Frontend API & Integration | ✅ | — | ✅ Complete |
| 9 | Database & Prompt | ✅ | — | ✅
| 10 | Appearance Selection UX | ✅ | — | ✅ Complete |
| 11 | Scene Details Save UX | ⬜ | — | ⬜ Not Started |
| ✓ | Testing & Verification | ⬜ | — | ⬜ Not Started |

**Legend:** ⬜ Not Started | 🔄 In Progress | ✅ Complete | — Not Applicable

---

### Documentation Files to Update (Summary)

| Doc File | Phase | Changes |
|----------|-------|---------|
| `docs/docs/api/endpoints/core.md` | 1-2 | Add appearance enums to `/enums` |
| `docs/docs/database/models/identity.md` | 3 | Add clothing, mood, setting fields |
| `docs/docs/api/endpoints/identities.md` | 3 | Add scene fields to API docs |
| `docs/docs/database/models/users.md` | 4 | Add 7 appearance fields |
| `docs/docs/api/endpoints/users.md` | 4 | Add appearance fields to API docs |
| `docs/docs/core-systems/prompt-manager/context-keys/appearance-context.md` | 5 | **NEW** - Appearance context key |
| `docs/docs/core-systems/prompt-manager/context-keys/scene-context.md` | 5 | **NEW** - Scene context key |
| `docs/docs/core-systems/prompt-manager/context-keys/overview.md` | 5 | Add new context keys |
| `sidebars.ts` | 5 | Add new context key docs to sidebar |

---

## Testing Plan

### Backend Tests
- Unit tests for each appearance enum
- Unit test for `get_appearance_context()` with various combinations
- Unit test for `get_scene_context()` with various combinations
- Integration test for generate_image endpoint with appearance + scene data

### Frontend Tests
- Component tests for each badge selector
- Component tests for scene text inputs
- Hook tests for `useUserAppearance`
- Integration test for Images page with appearance selection + scene inputs

### E2E Tests
- Full flow: select appearance → select identity → fill scene inputs → generate image → verify prompt includes all context

---

## Future Considerations

1. **Hair Style** - Could add as separate option (short, long, curly, etc.)
2. **Facial Hair** - For male-presenting options
3. **Accessories** - Glasses, etc.
4. **Multiple Appearance Profiles** - Let users save different "looks"
5. **AI-suggested Appearance** - Auto-detect from reference images
6. **Visualization Field Integration** - The existing `visualization` field on Identity is a free-form description. Consider how it relates to the new structured scene fields (clothing, mood, setting). Options:
   - Keep both (visualization for AI-generated descriptions, scene fields for user input)
   - Auto-populate scene fields from visualization text
   - Deprecate visualization in favor of structured fields
7. **Settings Page** - Build dedicated Settings page with Appearance section where users can manage their visualization preferences