---
sidebar_position: 1
---

# Overview

Context keys are the data points that can be injected into prompt templates to provide personalized and dynamic content. Each context key represents a specific piece of information about the user, their coaching state, or their conversation history.

## What Are Context Keys?

Context keys are enumerated values that define what data should be included in a prompt. When a prompt template specifies required context keys, the Prompt Manager automatically gathers the corresponding data and injects it into the template.

## Context Key Categories

Context keys are organized into logical categories based on their purpose and data source:

### User Context

Basic user information and profile data:

- `user_name`: User's display name
- `user_notes`: User's personal notes and preferences

### Identity Context

Information about the user's identities:

- `identities`: All user identities formatted as text
- `number_of_identities`: Count of user's identities
- `identity_focus`: Currently focused identity
- `current_identity`: Currently selected identity
- `focused_identities`: List of focused identities
- `refinement_identities`: Identities in refinement phase
- `affirmation_identities`: Identities with affirmations
- `visualization_identities`: Identities with visualizations

### Coaching Context

Current coaching state and progress:

- `current_phase`: Current coaching phase name
- `who_you_are`: User's self-description
- `who_you_want_to_be`: User's aspirational description
- `asked_questions`: Questions previously asked

### Conversation Context

Chat history and message data:

- `current_message`: The user's current message
- `previous_message`: The previous message in conversation
- `recent_messages`: Recent chat messages

### Process Context

Phase-specific process information:

- `brainstorming_category_context`: Context for identity brainstorming

## Phase-Specific Context

Some context keys provide different data depending on the current coaching phase:

### Identity Brainstorming Phase

- `brainstorming_category_context`: Provides category-specific context for identity brainstorming

### Identity Refinement Phase

- `refinement_identities`: Shows identities currently being refined

### Identity Affirmation Phase

- `affirmation_identities`: Shows identities with affirmations

### Identity Visualization Phase

- `visualization_identities`: Shows identities with visualizations

## How Context Keys Work

### 1. Template Specification

Prompts specify which context keys they need:

```python
prompt.required_context_keys = [
    ContextKey.USER_NAME,
    ContextKey.IDENTITIES,
    ContextKey.CURRENT_PHASE
]
```

### 2. Data Gathering

The Prompt Manager calls the appropriate context function for each key:

```python
def get_context_value(key: ContextKey, coach_state: CoachState):
    if key == ContextKey.USER_NAME:
        return get_user_name_context(coach_state)
    elif key == ContextKey.IDENTITIES:
        return get_identities_context(coach_state)
    # ... additional handlers
```

### 3. Template Injection

Context data is injected into the prompt template:

```markdown
You are helping {{user_name}} with {{current_phase}}.

Current Identities: {{identities}}
```

## Context Key Implementation

Each context key has a dedicated function that:

1. **Retrieves data** from the appropriate database models
2. **Formats the data** into readable text
3. **Returns the formatted string** for template injection

### Example Implementation

```python
def get_identities_context(coach_state: CoachState) -> str:
    identities = Identity.objects.filter(user=coach_state.user)
    if not identities.exists():
        return "No identities created yet."

    formatted_identities = []
    for identity in identities:
        formatted_identities.append(f"- {identity.name}: {identity.description}")

    return "\n".join(formatted_identities)
```

## Benefits of Context Keys

### Dynamic Content

- Prompts automatically include current user data
- No need to manually update prompt content
- Real-time personalization

### Consistent Formatting

- Standardized data formatting across all prompts
- Consistent user experience
- Easy to maintain and update

### Flexible Usage

- Prompts can request only the context they need
- Efficient data gathering
- Scalable to new context types

## Adding New Context Keys

To add a new context key:

1. **Add to ContextKey enum** in `server/enums/context_keys.py`
2. **Create context function** in `server/services/prompt_manager/utils/context.py`
3. **Add to get_context_value** function
4. **Update PromptContext model** if needed
5. **Document the new key** in the appropriate category

## Related Documentation

For detailed information about specific context keys, see the individual context key documentation in the sidebar.
