# Core

## Base URL

`/core/`

---

## Endpoints

### 1. Get Enums

- **URL:** `/core/enums/`
- **Method:** `GET`
- **Description:** Returns all enum values used throughout the application for populating dropdowns and select components in the frontend. This endpoint is primarily used by the Prompts management interface to populate form dropdowns.
- **Authentication:** Required
- **Response:**
  - `200 OK`: Object containing all enum values with their display labels.

#### Example Response

```json
{
  "coaching_phases": [
    {
      "value": "INTRODUCTION",
      "label": "Introduction"
    },
    {
      "value": "GET_TO_KNOW_YOU",
      "label": "Get To Know You"
    },
    {
      "value": "IDENTITY_CREATION",
      "label": "Identity Creation"
    },
    {
      "value": "IDENTITY_REFINEMENT",
      "label": "Identity Refinement"
    },
    {
      "value": "INTEGRATION",
      "label": "Integration"
    }
  ],
  "allowed_actions": [
    {
      "value": "CREATE_IDENTITY",
      "label": "Create Identity"
    },
    {
      "value": "UPDATE_IDENTITY",
      "label": "Update Identity"
    },
    {
      "value": "TRANSITION_PHASE",
      "label": "Transition Phase"
    },
    {
      "value": "SELECT_IDENTITY_FOCUS",
      "label": "Select Identity Focus"
    },
    {
      "value": "UPDATE_WHO_YOU_ARE",
      "label": "Update Who You Are"
    },
    {
      "value": "UPDATE_WHO_YOU_WANT_TO_BE",
      "label": "Update Who You Want To Be"
    },
    {
      "value": "ADD_USER_NOTE",
      "label": "Add User Note"
    }
  ],
  "context_keys": [
    {
      "value": "user_name",
      "label": "User Name"
    },
    {
      "value": "coaching_phase",
      "label": "Coaching Phase"
    },
    {
      "value": "current_identity",
      "label": "Current Identity"
    },
    {
      "value": "proposed_identity",
      "label": "Proposed Identity"
    },
    {
      "value": "who_you_are",
      "label": "Who You Are"
    },
    {
      "value": "who_you_want_to_be",
      "label": "Who You Want To Be"
    },
    {
      "value": "asked_questions",
      "label": "Asked Questions"
    },
    {
      "value": "user_goals",
      "label": "User Goals"
    }
  ]
}
```

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
2. **Hook makes API call** → `GET /core/enums/`
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
