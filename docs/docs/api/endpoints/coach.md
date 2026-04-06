# Coach

## Base URL

`/api/v1/coach`

---

## Endpoints

### 1. Process Message

- **URL:** `/api/v1/coach/process-message`
- **Method:** `POST`
- **Description:** Process a user message and return a coach response. This is the main endpoint for the coaching chatbot functionality. It handles the complete flow from user input to coach response, including state management and action execution.
- **Authentication:** Required
- **Request Body:**
  ```json
  {
    "message": "Hi, I'd like to start my coaching journey",
    "model_name": "gpt-4o",
    "actions": [
      {
        "action": "transition_phase",
        "params": { "to_phase": "get_to_know_you" }
      }
    ]
  }
  ```

  | Field | Type | Required | Description |
  |-------|------|----------|-------------|
  | `message` | string | Conditional | User's message to the coach. May be omitted if `actions` is non-empty. |
  | `model_name` | string | Optional | AI model to use (defaults to GPT-4o). |
  | `actions` | array | Optional | List of actions to execute. Each item has `action` (str) and `params` (object). At least one of `message` or `actions` must be provided. |

- **Response:**
  - `200 OK`: Coach response (see `CoachResponseSerializer`).
  - `400 Bad Request`: Validation errors.
  - `500 Internal Server Error`: Processing error.

#### Example Response

```json
{
  "message": "Welcome to your coaching journey! I'm excited to help you discover and develop your identities. Let's start by understanding who you are and who you want to become. What brings you here today?",
  "final_prompt": "You are a life coach helping users develop their identities...",
  "component": {
    "type": "canned_response",
    "options": ["Tell me more", "Let's begin"]
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | Coach's response message. |
| `final_prompt` | string | The final prompt used to generate the coach's response. |
| `component` | object (optional) | Optional component configuration for frontend rendering. Only present when the coach response triggers a UI component. |

---

### 2. Process Message for User (Admin Only)

- **URL:** `/api/v1/admin/coach/process-message-for-user`
- **Method:** `POST`
- **Description:** Process a message as if sent by a specific user. This endpoint allows admin users to simulate coaching conversations for specific users, primarily used for testing and debugging purposes.
- **Authentication:** Required (IsAdminUser — is_staff OR is_superuser)
- **Request Body:**
  ```json
  {
    "user_id": "specific-user-uuid",
    "message": "Hi, I'd like to start my coaching journey",
    "model_name": "gpt-4o",
    "actions": []
  }
  ```
- **Response:**
  - `200 OK`: Same response format as the main process-message endpoint (`message`, `final_prompt`, `component`).
  - `400 Bad Request`: Validation errors or missing user_id.
  - `404 Not Found`: User not found.
  - `500 Internal Server Error`: Processing error.

#### Example Response

Same format as the main process-message endpoint.

---

## How It Works

### Step-by-Step Process

1. **Authentication & Validation**
   - Validates user authentication
   - Parses and validates the incoming request using `CoachRequestSerializer`
   - At least one of `message` or `actions` must be provided

2. **Chat History Management**
   - Ensures chat history starts with initial bot message if empty
   - Adds the user's message to the chat history

3. **State Retrieval**
   - Retrieves the user's current `CoachState` from the database

4. **Prompt Generation**
   - Uses `PromptManager` to build the appropriate prompt based on current coaching phase
   - Includes recent chat history for context

5. **AI Processing**
   - Calls the AI service (default: GPT-4o) with the generated prompt
   - Processes the AI response

6. **Action Execution**
   - Extracts actions from the AI response (and any request-provided actions)
   - Applies actions to update the coach state and related models
   - Records actions in the database

7. **Response Assembly**
   - Returns the coach's message, the final prompt used, and an optional component configuration
   - The frontend fetches updated state separately via `/api/v1/user/me/complete`

### Key Components

- **PromptManager**: Builds context-aware prompts based on coaching phase
- **ActionHandler**: Executes actions like phase transitions, identity creation, etc.
- **AIService**: Handles communication with AI models
- **StateManagement**: Maintains coaching session state across conversations

---

## Field Reference

For detailed field information on models used in these endpoints, see:

- **[Coach State Fields](../../database/models/coach-state)** - Coach state structure
- **[Identity Fields](../../database/models/identity)** - Identity model structure
- **[Chat Message Fields](../../database/models/chat-message)** - Chat message structure
- **[Action Fields](../../database/models/action)** - Action model structure

---

## Notes

- The main endpoint uses the authenticated user by default.
- The admin endpoint (`/api/v1/admin/coach/process-message-for-user`) allows processing messages for specific users (useful for testing). It requires IsAdminUser permission (is_staff OR is_superuser).
- The response does NOT include coach_state, actions, chat_history, or identities. The frontend fetches updated state separately.
- Actions are automatically executed and recorded for audit purposes.
- The system supports multiple AI models, with GPT-4o as the default.
- Update this document whenever the API changes.
