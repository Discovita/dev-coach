# Core API Documentation

## Base URL

`/core`

---

## Endpoints

### 1. Get All Enum Values

- **URL:** `/core/enums/`
- **Method:** `GET`
- **Description:** Returns all enum values for coach_state, allowed_actions, and context_keys. Used for populating dropdowns/selects in the frontend prompt management UI.
- **Response:**
  - `200 OK`: Object containing lists of enum values and labels.

#### Example Response

```json
{
  "coaching_phases": [
    { "value": "introduction", "label": "Introduction" },
    { "value": "identity_brainstorming", "label": "Identity Brainstorming" },
    { "value": "identity_refinement", "label": "Identity Refinement" }
  ],
  "allowed_actions": [
    { "value": "create_identity", "label": "Create Identity" },
    { "value": "update_identity", "label": "Update Identity" },
    { "value": "accept_identity", "label": "Accept Identity" },
    {
      "value": "accept_identity_refinement",
      "label": "Accept Identity Refinement"
    },
    { "value": "add_identity_note", "label": "Add Identity Note" },
    { "value": "transition_state", "label": "Transition State" },
    { "value": "select_identity_focus", "label": "Select Identity Focus" }
  ],
  "context_keys": [
    { "value": "user_name", "label": "User Name" },
    { "value": "number_of_identities", "label": "Number of Identities" },
    {
      "value": "current_identity_description",
      "label": "Current Identity Description"
    },
    { "value": "identities_summary", "label": "Identities Summary" },
    { "value": "phase", "label": "Phase" }
  ]
}
```

---

## Notes

- All enum values are sourced from the backend enums in `server/enums/`.
- This endpoint is intended for use by frontend forms and UI components that need to display valid options for prompts and related features.
- Update this document whenever the API changes or new enums are added.
