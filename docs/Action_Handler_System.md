# Action Handler System Documentation

## Overview

The action handler system is responsible for processing and applying a set of user or AI-driven "actions" to the coaching state within the Discovita platform. Actions represent discrete, atomic operations that can modify user identities, coaching state, or related data. The system is designed for extensibility, type safety, and clear separation of concerns.

---

## Directory Structure

- `handler.py`: Main entry point for applying actions to a `CoachState`.
- `models/`: Contains Pydantic models for action parameters and action objects.
- `utils/`: Utility modules for dynamic schema generation and action instructions.
- `actions/`: Implementation of each supported action as a function.

---

## Core Flow

### 1. **Action Application (`handler.py`)**

- **Purpose:** Orchestrates the application of all actions present in a `CoachChatResponse` to a `CoachState`.
- **Key Function:** `apply_actions(coach_state, response)`
  - Iterates over all non-None fields in the response (excluding the message).
  - For each action, determines the handler function and applies it to the state.
  - Logs each step for traceability.
  - Returns the updated `CoachState` and a list of actions applied.

#### Step-by-step in `apply_actions`:
1. Log the start of action application.
2. Iterate over each field in the response (excluding 'message').
3. For each action:
   - Extract parameters.
   - Log the action.
   - Call the corresponding handler function from `actions/`.
   - Append action details to the actions list.
4. Refresh the `CoachState` from the database to ensure the latest state.
5. Return the updated state and actions list.

---

### 2. **Action Models (`models/`)**

#### a. **Parameter Models (`params.py`)**
- **Purpose:** Define the structure and validation for parameters required by each action.
- **Usage:** Used as the `params` field in action models and passed to action handler functions.
- **Examples:**
  - `CreateIdentityParams`: Description, note, and category for a new identity.
  - `UpdateIdentityParams`: ID and new description for an identity.
  - `TransitionStateParams`: Target coaching state.

#### b. **Action Models (`actions.py`)**
- **Purpose:** Wrap parameter models in a Pydantic model for type safety and schema generation.
- **Usage:** Used in dynamic response schemas and for validation in the handler.
- **Examples:**
  - `CreateIdentityAction`: Contains `params: CreateIdentityParams`.
  - `AddIdentityNoteAction`: Contains `params: AddIdentityNoteParams`.

#### c. **Exports (`__init__.py`)**
- **Purpose:** Exposes all parameter and action models for import elsewhere in the system.

---

### 3. **Action Implementations (`actions/`)**

Each file in this directory implements a single action as a function. All functions:
- Take a `CoachState` and the relevant params model as arguments.
- Perform the required database updates or business logic.
- Are mapped to action types in the handler.

**Examples:**
- `create_identity`: Creates a new identity and links it to the user.
- `update_identity`: Updates the description of an existing identity.
- `accept_identity`: Marks an identity as accepted.
- `add_identity_note`: Appends a note to an identity's notes list.
- `transition_state`: Changes the current coaching state.
- `select_identity_focus`: Updates the focus category for the coach state.

---

### 4. **Utilities (`utils/`)**

#### a. **Dynamic Schema Generation (`dynamic_schema.py`)**
- **Purpose:** Dynamically builds a Pydantic model for the response format, including only the allowed actions.
- **Usage:** Used for runtime validation and schema generation for AI or frontend consumption.
- **Key Function:** `build_dynamic_response_format(allowed_actions)`

#### b. **Action Instructions (`action_instructions.py`)**
- **Purpose:** Provides structured, markdown-formatted instructions and JSON schemas for each action.
- **Usage:** Used in prompt generation for AI models or documentation for frontend developers.
- **Key Function:** `get_action_instructions(action_types)`

---

## Type and Model Documentation

### Parameter Models (in `models/params.py`)
- **Purpose:** Define the required and optional fields for each action.
- **Used in:** Action models (`models/actions.py`), action handler functions (`actions/`), and dynamic schema generation (`utils/dynamic_schema.py`).

### Action Models (in `models/actions.py`)
- **Purpose:** Encapsulate parameter models for each action, enabling type-safe, schema-driven action handling.
- **Used in:** Dynamic response schemas, action handler, and prompt instructions.

---

## Extending the System

To add a new action:
1. **Define a parameter model** in `models/params.py`.
2. **Create an action model** in `models/actions.py` that wraps the parameter model.
3. **Implement the action function** in `actions/`, following the existing pattern.
4. **Register the action** in:
   - The handler's `ACTION_HANDLERS` mapping.
   - The dynamic schema and instructions utilities if needed.

---

## Summary

The action handler system is modular, type-safe, and designed for extensibility. Each action is clearly defined, validated, and applied in a consistent manner, with comprehensive logging and schema support for both backend and AI-driven workflows. 