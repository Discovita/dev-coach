# Prompt Manager System Documentation

## Overview

The prompt manager system is responsible for constructing, formatting, and managing prompts for the coach chatbot service. It gathers user and session context, applies system and identity instructions, and formats prompts for different LLM providers. The system is modular, extensible, and designed to support evolving requirements for prompt engineering and context management.

---

## Directory Structure

- `manager.py`: Main entry point for prompt construction and formatting.
- `models/`: Contains Pydantic models for prompt context.
- `utils/`: Utility modules for context gathering, logging, formatting, and instruction management.
- `prompts/`: Markdown files containing reusable system and identity instructions.

---

## Core Flow

### 1. **Prompt Construction (`manager.py`)**

- **Purpose:** Orchestrates the creation of a complete prompt for the chat endpoint, including context, instructions, and formatting for the target LLM provider.
- **Key Class:** `PromptManager`
  - **Key Method:** `create_chat_prompt(user, model, version_override=None)`
    - Retrieves the user's `CoachState`.
    - Selects the appropriate prompt template for the current state (optionally overridden by version).
    - Gathers all required context for the prompt.
    - Determines the LLM provider and builds the response format schema.
    - Formats the prompt for the provider, including context and response format.
    - Prepends system context and appends action instructions.
    - Returns the fully constructed prompt and response format.

#### Step-by-step in `create_chat_prompt`:
1. Retrieve the user's `CoachState`.
2. Select the newest active prompt for the current state (or use version override).
3. Gather all required context for the prompt.
4. Determine the LLM provider.
5. Build the dynamic response format model for allowed actions.
6. Format the prompt for the provider, including context and response format.
7. Prepend system context from markdown.
8. Append action instructions for allowed actions.
9. Return the constructed prompt and response format.

---

### 2. **Prompt Context Models (`models/`)**

#### a. **PromptContext (`prompt_context.py`)**
- **Purpose:** Encapsulates all context data used to format prompt templates for the coach chatbot.
- **Fields:** Includes user name, recent messages, identities, current focus, and more.
- **Usage:** Used by the prompt manager and context gathering utilities to ensure all required context is available for prompt construction.

#### b. **Exports (`__init__.py`)**
- **Purpose:** Exposes the `PromptContext` model for import elsewhere in the system.

---

### 3. **Utilities (`utils/`)**

#### a. **Context Gathering (`context_gathering.py`)**
- **Purpose:** Gathers all required context values for a given prompt and coach state.
- **Key Function:** `gather_prompt_context(prompt, coach_state)`
  - Iterates over required context keys and fetches values from the database or models.
  - Returns a populated `PromptContext` object.

#### b. **Context Logging (`context_logging.py`)**
- **Purpose:** Logs a summary of the current prompt context for debugging and development.
- **Key Function:** `log_context_stats(prompt_context)`

#### c. **Prompt Formatting (`format_for_provider.py`)**
- **Purpose:** Formats a prompt for a specific LLM provider, applying provider-specific rules and including the response format schema if needed.
- **Key Function:** `format_for_provider(prompt, prompt_context, provider, response_format)`

#### d. **Action Instructions (`append_action_instructions.py`)**
- **Purpose:** Appends action instructions (with JSON schemas) to the system message for prompt generation.
- **Key Function:** `append_action_instructions(system_message, allowed_actions)`

#### e. **System Context (`prepend_system_context.py`)**
- **Purpose:** Prepends system context from a markdown file to the system message for prompt generation.
- **Key Function:** `prepend_system_context(system_message)`

---

### 4. **Prompt Templates (`prompts/`)**

- **system_context.md:** Contains the core coaching philosophy, process, communication guidelines, and state transition rules. Prepended to every prompt.
- **identity_instructions.md:** Contains guidelines for identity creation and category definitions. Used to guide identity-related prompt construction.

---

## Type and Model Documentation

### PromptContext (in `models/prompt_context.py`)
- **Purpose:** Defines all fields required for prompt construction, including user and session-specific data.
- **Used in:** Context gathering, prompt formatting, and logging utilities.

---

## Extending the System

To add new context or prompt features:
1. **Add new fields** to `PromptContext` as needed.
2. **Update context gathering logic** in `utils/context_gathering.py` to fetch and populate new fields.
3. **Update prompt templates** in `prompts/` to utilize new context fields.
4. **Add or update utility functions** in `utils/` for new formatting or instruction requirements.

---

## Summary

The prompt manager system is modular, extensible, and designed for robust prompt engineering. It centralizes context gathering, instruction management, and provider-specific formatting, ensuring that all prompts are constructed with the necessary context and guidance for high-quality LLM responses. 