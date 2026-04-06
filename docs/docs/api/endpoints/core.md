# Core

## Base URL

`/api/v1/core`

---

## Endpoints

### 1. Get Enums

- **URL:** `/api/v1/core/enums`
- **Method:** `GET`
- **Description:** Returns all enum values used throughout the application for populating dropdowns and select components in the frontend. This endpoint is primarily used by the Prompts management interface to populate form dropdowns, and by the Images page for appearance customization options.
- **Authentication:** Required
- **Response:**
  - `200 OK`: Object containing all enum values with their display labels.

#### Example Response

```json
{
  "coaching_phases": [
    { "value": "system_context", "label": "System Context" },
    { "value": "introduction", "label": "Introduction" },
    { "value": "get_to_know_you", "label": "Get to Know You" },
    { "value": "identity_warm_up", "label": "Identity Warm-Up" },
    { "value": "identity_brainstorming", "label": "Identity Brainstorming" },
    { "value": "brainstorming_review", "label": "Brainstorming Review" },
    { "value": "identity_refinement", "label": "Identity Refinement" },
    { "value": "anything_missing", "label": "Anything Missing" },
    { "value": "identity_commitment", "label": "Identity Commitment" },
    { "value": "i_am_statement", "label": "I Am Statement" },
    { "value": "identity_visualization", "label": "Identity Visualization" }
  ],
  "allowed_actions": [
    { "value": "create_identity", "label": "Create Identity" },
    { "value": "create_multiple_identities", "label": "Create Multiple Identities" },
    { "value": "update_identity", "label": "Update Identity" },
    { "value": "update_identity_name", "label": "Update Identity Name" },
    { "value": "update_i_am_statement", "label": "Update I Am Statement" },
    { "value": "update_identity_visualization", "label": "Update Identity Visualization" },
    { "value": "accept_identity", "label": "Accept Identity" },
    { "value": "accept_identity_refinement", "label": "Accept Identity Refinement" },
    { "value": "accept_identity_commitment", "label": "Accept Identity Commitment" },
    { "value": "accept_i_am_statement", "label": "Accept I Am Statement" },
    { "value": "accept_identity_visualization", "label": "Accept Identity Visualization" },
    { "value": "archive_identity", "label": "Archive Identity" },
    { "value": "nest_identity", "label": "Nest Identity" },
    { "value": "add_identity_note", "label": "Add Identity Note" },
    { "value": "transition_phase", "label": "Transition Phase" },
    { "value": "select_identity_focus", "label": "Select Identity Focus" },
    { "value": "skip_identity_category", "label": "Skip Identity Category" },
    { "value": "unskip_identity_category", "label": "Unskip Identity Category" },
    { "value": "update_who_you_are", "label": "Update Who You Are" },
    { "value": "update_who_you_want_to_be", "label": "Update Who You Want to Be" },
    { "value": "update_asked_questions", "label": "Update Asked Questions" },
    { "value": "set_current_identity", "label": "Set Current Identity" },
    { "value": "combine_identities", "label": "Combine Identities" },
    { "value": "add_user_note", "label": "Add User Note" },
    { "value": "update_user_note", "label": "Update User Note" },
    { "value": "delete_user_note", "label": "Delete User Note" }
  ],
  "context_keys": [
    { "value": "user_name", "label": "User Name" },
    { "value": "identities", "label": "Identities" },
    { "value": "number_of_identities", "label": "Number of Identities" },
    { "value": "identity_focus", "label": "Identity Focus" },
    { "value": "who_you_are", "label": "Who You Are" },
    { "value": "who_you_want_to_be", "label": "Who You Want to Be" },
    { "value": "focused_identities", "label": "Focused Identities" },
    { "value": "user_notes", "label": "User Notes" },
    { "value": "current_message", "label": "Current Message" },
    { "value": "previous_message", "label": "Previous Message" },
    { "value": "current_phase", "label": "Current Phase" },
    { "value": "brainstorming_category_context", "label": "Brainstorming Category Context" },
    { "value": "current_identity", "label": "Current Identity" },
    { "value": "asked_questions", "label": "Asked Questions" },
    { "value": "refinement_identities", "label": "Refinement Identities" },
    { "value": "commitment_identities", "label": "Commitment Identities" },
    { "value": "i_am_identities", "label": "I Am Identities" },
    { "value": "visualization_identities", "label": "Visualization Identities" },
    { "value": "identity_ids", "label": "Identity IDs" },
    { "value": "identity_for_image", "label": "Identity for Image" }
  ],
  "prompt_types": [
    { "value": "coach", "label": "Coach" },
    { "value": "sentinel", "label": "Sentinel" },
    { "value": "system", "label": "System" },
    { "value": "image_generation", "label": "Image Generation" }
  ],
  "appearance": {
    "genders": [
      { "value": "man", "label": "Man" },
      { "value": "woman", "label": "Woman" },
      { "value": "person", "label": "Person" }
    ],
    "skin_tones": [
      { "value": "light", "label": "Light" },
      { "value": "medium_light", "label": "Medium-Light" },
      { "value": "medium", "label": "Medium" },
      { "value": "medium_dark", "label": "Medium-Dark" },
      { "value": "dark", "label": "Dark" }
    ],
    "hair_colors": [
      { "value": "black", "label": "Black" },
      { "value": "brown", "label": "Brown" },
      { "value": "blonde", "label": "Blonde" },
      { "value": "red", "label": "Red" },
      { "value": "auburn", "label": "Auburn" },
      { "value": "gray", "label": "Gray" },
      { "value": "white", "label": "White" },
      { "value": "bald", "label": "Bald" }
    ],
    "eye_colors": [
      { "value": "brown", "label": "Brown" },
      { "value": "blue", "label": "Blue" },
      { "value": "green", "label": "Green" },
      { "value": "hazel", "label": "Hazel" },
      { "value": "gray", "label": "Gray" },
      { "value": "amber", "label": "Amber" }
    ],
    "heights": [
      { "value": "short", "label": "Short" },
      { "value": "below_average", "label": "Below Average" },
      { "value": "average", "label": "Average" },
      { "value": "above_average", "label": "Above Average" },
      { "value": "tall", "label": "Tall" }
    ],
    "builds_male": [
      { "value": "...", "label": "..." }
    ],
    "builds_female": [
      { "value": "...", "label": "..." }
    ],
    "builds_neutral": [
      { "value": "...", "label": "..." }
    ],
    "age_ranges": [
      { "value": "twenties", "label": "Young Adult (20s)" },
      { "value": "thirties", "label": "In Their 30s" },
      { "value": "forties", "label": "In Their 40s" },
      { "value": "fifties", "label": "Middle-Aged (50s)" },
      { "value": "sixty_plus", "label": "Mature (60+)" }
    ]
  }
}
```

**Note:** The `builds` field is split into three gender-specific arrays: `builds_male`, `builds_female`, and `builds_neutral`. Each contains build options appropriate for that gender selection. The `prompt_types` key is also included in the response.

---

## Frontend Usage

### Prompts Management Interface

This endpoint is primarily used by the Prompts management page (`/prompts`) to populate form dropdowns and select components. Here's how it's integrated:

#### 1. **Coaching Phase Dropdown**
- **Purpose**: Select which coaching phase the prompt is associated with
- **Usage**: When creating or editing a prompt, users select from available coaching phases
- **Data Source**: `coaching_phases` array from the enums response
- **Frontend Component**: Dropdown/select component populated with `value` and `label` pairs

#### 2. **Allowed Actions Multi-Select**
- **Purpose**: Choose which actions the coach can perform when using this prompt
- **Usage**: Multi-select component allowing users to choose multiple allowed actions
- **Data Source**: `allowed_actions` array from the enums response
- **Frontend Component**: Multi-select or checkbox group component

#### 3. **Required Context Keys Multi-Select**
- **Purpose**: Specify which context keys are required for this prompt to function
- **Usage**: Multi-select component for choosing required context data
- **Data Source**: `context_keys` array from the enums response
- **Frontend Component**: Multi-select or checkbox group component

#### 4. **Appearance Options (Images Page)**
- **Purpose**: Provide appearance customization options for identity image generation
- **Usage**: Badge selectors on the Images page for user appearance preferences
- **Data Source**: `appearance` object containing arrays for genders, skin_tones, hair_colors, eye_colors, heights, builds, and age_ranges
- **Frontend Component**: Badge selector components with visual swatches for skin tones

### Frontend Implementation

The frontend uses a custom hook (`useCoreEnums`) to fetch and cache this data:

```typescript
// Example usage in Prompts.tsx
import { useCoreEnums } from "@/hooks/use-core";

function PromptsPage() {
  const { coachingPhases, allowedActions, contextKeys } = useCoreEnums();
  
  return (
    <form>
      <select>
        {coachingPhases.map(phase => (
          <option key={phase.value} value={phase.value}>
            {phase.label}
          </option>
        ))}
      </select>
      
      <MultiSelect
        options={allowedActions}
        valueKey="value"
        labelKey="label"
      />
      
      <MultiSelect
        options={contextKeys}
        valueKey="value"
        labelKey="label"
      />
    </form>
  );
}
```

### Data Flow

1. **Frontend loads Prompts page** → Calls `useCoreEnums()` hook
2. **Hook makes API call** → `GET /api/v1/core/enums`
3. **Backend returns enum data** → All available values with labels
4. **Frontend caches data** → Stores in React Query cache for performance
5. **Components render** → Dropdowns populated with cached enum data
6. **User interactions** → Form submissions use the `value` field, display uses `label` field

### Benefits

- **Consistency**: All enum values are centrally managed
- **Performance**: Data is cached and reused across components
- **Maintainability**: Adding new enum values only requires backend changes
- **User Experience**: Clear, human-readable labels for all options
- **Type Safety**: Frontend can validate selections against known values

---

## Notes

- This endpoint is essential for the Prompts management interface functionality.
- The response format with `value`/`label` pairs is designed for easy integration with frontend form components.
- All enum values are sourced from the backend enum classes to ensure consistency.
- The frontend caches this data to avoid repeated API calls.
- Update this document whenever new enum values are added to the system.
