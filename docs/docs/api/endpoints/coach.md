# Coach

## Base URL

`/coach/`

---

## Endpoints

### 1. Process Message

- **URL:** `/coach/process-message/`
- **Method:** `POST`
- **Description:** Process a user message and return a coach response. This is the main endpoint for the coaching chatbot functionality. It handles the complete flow from user input to coach response, including state management and action execution.
- **Authentication:** Required
- **Request Body:**
  ```json
  {
    "message": "Hi, I'd like to start my coaching journey",
    "model_name": "gpt-4o"
  }
  ```
- **Response:**
  - `200 OK`: Coach response with updated state and actions.
  - `400 Bad Request`: Validation errors.
  - `404 Not Found`: Coach state not found.

#### Example Response

```json
{
  "message": "Welcome to your coaching journey! I'm excited to help you discover and develop your identities. Let's start by understanding who you are and who you want to become. What brings you here today?",
  "coach_state": {
    "id": "uuid-string",
    "user": "user-uuid",
    "current_phase": "INTRODUCTION",
    "current_identity": null,
    "proposed_identity": null,
    "identity_focus": "PASSIONS",
    "skipped_identity_categories": [],
    "who_you_are": [],
    "who_you_want_to_be": [],
    "asked_questions": [],
    "updated_at": "2024-06-01T12:00:00Z"
  },
  "final_prompt": "You are a life coach helping users develop their identities...",
  "actions": [
    {
      "action_type": "TRANSITION_PHASE",
      "parameters": {
        "from_phase": "INTRODUCTION",
        "to_phase": "GET_TO_KNOW_YOU"
      },
      "result_summary": "Successfully transitioned from Introduction to Get To Know You phase"
    }
  ],
  "chat_history": [
    {
      "id": "uuid-string",
      "role": "COACH",
      "content": "Welcome to Dev Coach! I'm here to help you...",
      "timestamp": "2024-06-01T12:00:00Z"
    },
    {
      "id": "uuid-string",
      "role": "USER",
      "content": "Hi, I'd like to start my coaching journey",
      "timestamp": "2024-06-01T12:01:00Z"
    },
    {
      "id": "uuid-string",
      "role": "COACH",
      "content": "Welcome to your coaching journey! I'm excited to help you discover and develop your identities...",
      "timestamp": "2024-06-01T12:01:30Z"
    }
  ],
  "identities": [
    {
      "id": "uuid-string",
      "user": "user-uuid",
      "name": "Creative Visionary",
      "affirmation": "I am a bold creator, transforming ideas into reality.",
      "visualization": "I see myself confidently presenting innovative solutions...",
      "state": "ACCEPTED",
      "notes": ["Note 1", "Note 2"],
      "category": "PASSIONS",
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-06-01T12:00:00Z"
    }
  ]
}
```

---

### 2. Process Message for User (Admin Only)

- **URL:** `/coach/process-message-for-user/`
- **Method:** `POST`
- **Description:** Process a message as if sent by a specific user. This endpoint allows admin users to simulate coaching conversations for specific users, primarily used for testing and debugging purposes.
- **Authentication:** Required (Admin/Superuser only)
- **Request Body:**
  ```json
  {
    "message": "Hi, I'd like to start my coaching journey",
    "model_name": "gpt-4o",
    "user_id": "specific-user-uuid"
  }
  ```
- **Response:**
  - `200 OK`: Coach response with updated state and actions.
  - `400 Bad Request`: Validation errors or missing user_id.
  - `403 Forbidden`: Not authorized (not admin/superuser).
  - `404 Not Found`: User or coach state not found.

#### Example Response

Same format as the main process-message endpoint.

---

## How It Works

### Step-by-Step Process

1. **Authentication & Validation**
   - Validates user authentication
   - Parses and validates the incoming request using `CoachRequestSerializer`

2. **Chat History Management**
   - Ensures chat history starts with initial bot message if empty
   - Adds the user's message to the chat history

3. **State Retrieval**
   - Retrieves the user's current `CoachState` from the database
   - Returns 404 if no coach state exists

4. **Prompt Generation**
   - Uses `PromptManager` to build the appropriate prompt based on current coaching phase
   - Includes recent chat history (last 5 messages) for context

5. **AI Processing**
   - Calls the AI service (default: GPT-4o) with the generated prompt
   - Processes the AI response using `CoachChatResponse` model

6. **Action Execution**
   - Extracts actions from the AI response
   - Applies actions to update the coach state and related models
   - Records actions in the database

7. **Response Assembly**
   - Serializes the updated coach state
   - Includes the latest chat history (last 20 messages)
   - Returns all user identities
   - Formats the complete response

### Key Components

- **PromptManager**: Builds context-aware prompts based on coaching phase
- **ActionHandler**: Executes actions like phase transitions, identity creation, etc.
- **AIService**: Handles communication with AI models
- **StateManagement**: Maintains coaching session state across conversations

---

## Field Reference

For detailed field information on models used in these endpoints, see:

- **[Coach State Fields](../models/coach-state.md)** - Coach state structure
- **[Identity Fields](../models/identity.md)** - Identity model structure
- **[Chat Message Fields](../models/chat-message.md)** - Chat message structure
- **[Action Fields](../models/action.md)** - Action model structure

---

## Notes

- The main endpoint uses the authenticated user by default.
- The admin endpoint allows processing messages for specific users (useful for testing).
- Chat history is automatically managed and includes the last 20 messages.
- Actions are automatically executed and recorded for audit purposes.
- The system supports multiple AI models, with GPT-4o as the default.
- All responses include the complete updated state for frontend synchronization.
- Update this document whenever the API changes.
