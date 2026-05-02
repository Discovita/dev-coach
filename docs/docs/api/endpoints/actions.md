# Actions

## Overview

Actions represent the operations that the coach performs during coaching sessions, such as creating identities, transitioning phases, or updating user data. **There is no standalone `/actions/` ViewSet.** Actions are accessed through the User and Test User endpoints.

**Important**: Actions are read-only records created by the system during coach message processing.

---

## Endpoints

### 1. Get Current User's Actions

- **URL:** `/api/v1/user/me/actions`
- **Method:** `GET`
- **Description:** Returns all actions performed for the authenticated user, ordered by most recent first.
- **Authentication:** Required
- **Response:**
  - `200 OK`: Array of action objects.

### 2. Get Test User's Actions (Admin Only)

- **URL:** `/api/v1/admin/test-user/{pk}/actions`
- **Method:** `GET`
- **Description:** Returns all actions performed for a specific user, ordered by most recent first.
- **Authentication:** Required (IsAdminUser — is_staff OR is_superuser)
- **Response:**
  - `200 OK`: Array of action objects.
  - `404 Not Found`: User not found.

---

## Response Format

Both endpoints return the same `ActionSerializer` format:

```json
[
  {
    "id": "uuid-string",
    "user": "user-uuid",
    "action_type": "transition_phase",
    "action_type_display": "Transition Phase",
    "parameters": {
      "from_phase": "introduction",
      "to_phase": "get_to_know_you"
    },
    "result_summary": "Successfully transitioned from Introduction to Get To Know You phase",
    "timestamp": "2024-06-01T12:00:00Z",
    "updated_at": "2024-06-01T12:00:00Z",
    "timestamp_formatted": "2024-06-01 12:00:00",
    "coach_message": {
      "id": "uuid-string",
      "role": "coach",
      "content": "Great! Let's move to the next phase...",
      "timestamp": "2024-06-01T12:00:00Z",
      "component_config": null
    },
    "test_scenario": null
  },
  {
    "id": "uuid-string",
    "user": "user-uuid",
    "action_type": "create_identity",
    "action_type_display": "Create Identity",
    "parameters": {
      "identity_name": "Creative Visionary",
      "category": "passions_and_talents"
    },
    "result_summary": "Created new identity: Creative Visionary",
    "timestamp": "2024-06-01T11:00:00Z",
    "updated_at": "2024-06-01T11:00:00Z",
    "timestamp_formatted": "2024-06-01 11:00:00",
    "coach_message": {
      "id": "uuid-string",
      "role": "coach",
      "content": "I've created a new identity for you...",
      "timestamp": "2024-06-01T11:00:00Z",
      "component_config": null
    },
    "test_scenario": null
  }
]
```

### ActionSerializer Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID (string) | Unique identifier for the action |
| `user` | UUID (string) | User ID this action belongs to |
| `action_type` | string | Action type enum value (lowercase). See [Action Types](#action-types). |
| `action_type_display` | string | Human-readable action type label |
| `parameters` | object | Action-specific parameters (JSON) |
| `result_summary` | string | Summary of the action result |
| `timestamp` | DateTime (ISO 8601) | When the action was created |
| `updated_at` | DateTime (ISO 8601) | When the action was last updated |
| `timestamp_formatted` | string | Formatted timestamp (YYYY-MM-DD HH:MM:SS) |
| `coach_message` | object or null | Nested ChatMessage that triggered this action |
| `test_scenario` | UUID or null | Associated test scenario ID, if any |

---

## Action Types

All action type values are lowercase strings (see `enums/action_type.py`):

### Identity Actions
- `create_identity`: Creates a new identity for the user
- `create_multiple_identities`: Creates multiple identities at once
- `update_identity`: Updates an existing identity
- `update_identity_name`: Updates an identity's name
- `update_i_am_statement`: Updates an identity's I Am statement
- `update_identity_visualization`: Updates an identity's visualization
- `accept_identity`: Accepts a proposed identity
- `accept_identity_refinement`: Accepts identity refinement
- `accept_identity_commitment`: Accepts identity commitment
- `accept_i_am_statement`: Accepts an I Am statement
- `accept_identity_visualization`: Accepts an identity visualization
- `archive_identity`: Archives an identity
- `nest_identity`: Nests an identity under another
- `add_identity_note`: Adds a note to an identity
- `combine_identities`: Combines two or more identities

### Phase & State Actions
- `transition_phase`: Moves the coaching session to a new phase
- `select_identity_focus`: Selects the identity category to focus on
- `skip_identity_category`: Marks an identity category as skipped
- `unskip_identity_category`: Un-skips a previously skipped identity category
- `set_current_identity`: Sets the current identity being worked on

### User Data Actions
- `update_who_you_are`: Updates the "who you are" list
- `update_who_you_want_to_be`: Updates the "who you want to be" list
- `update_asked_questions`: Updates the asked questions list
- `add_user_note`: Creates a note about the user (sentinel action)
- `update_user_note`: Updates a user note (sentinel action)
- `delete_user_note`: Deletes a user note (sentinel action)

### Component Actions
- `show_introduction_canned_response_component`: Shows introduction canned response UI
- `show_accept_i_am_component`: Shows accept I Am statement UI
- `show_suggest_i_am_statement_component`: Shows suggest I Am statement UI
- `show_i_am_statements_summary_component`: Shows I Am statements summary UI
- `show_combine_identities`: Shows combine identities UI
- `show_nest_identities`: Shows nest identities UI
- `show_archive_identity`: Shows archive identity UI

### Persistent Component Actions
- `persist_combine_identities`: Persists combine identities component
- `persist_nest_identities`: Persists nest identities component
- `persist_archive_identity`: Persists archive identity component
- `persist_suggest_i_am_statement_component`: Persists suggest I Am statement component
- `persist_i_am_statements_summary_component`: Persists I Am statements summary component

---

## Field Reference

For detailed field information on models used in these endpoints, see:

- **[Action Fields](/docs/database/models/action)** - Action model structure
- **[Chat Message Fields](/docs/database/models/chat-message)** - Chat message structure
- **[User Fields](/docs/database/models/users)** - User model structure

---

## Notes

- There is no standalone `/actions/` ViewSet. Actions are accessed via `/api/v1/user/me/actions` and `/api/v1/admin/test-user/{pk}/actions`.
- All action_type values in responses use lowercase stored values (e.g., `"create_identity"` not `"CREATE_IDENTITY"`).
- Actions are ordered by timestamp (newest first).
- Actions are read-only — they are created automatically during coach message processing.
- Each action may have a nested `coach_message` showing the message that triggered it.
- Update this document whenever the API changes.
