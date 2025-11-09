---
sidebar_position: 1
---

# Overview

The Identity Brainstorming Context provides specialized guidance for each of the 9 identity categories during the Identity Brainstorming phase.

## What It Provides

When a user is brainstorming identities for a specific category, the context includes:

- Category-specific approach and methodology
- Key questions to explore
- Natural resistance responses and how to handle them
- Language elevation techniques
- Transition guidance to the next category
- Skipping guidance where applicable

## How It Works

The context is injected into the Identity Brainstorming prompt based on the current `identity_focus` stored in the user's `CoachState`. This allows the AI to provide targeted, relevant guidance for each specific identity category without overwhelming the prompt with information for all categories.

## Implementation

The context is retrieved from markdown files stored in the `server/services/prompt_manager/utils/context/identity_category_context/` directory, with each category having its own dedicated file.

## Content Structure

Each category file contains:

- **Category Type**: Whether it's a single or multiple identity category
- **Key Distinctions**: What makes this category unique
- **Category-Specific Approach**: How to guide the user through this category
- **Key Questions**: Specific questions to explore with the user
- **Language Elevation**: How to transform limiting language into empowering identity language
- **Natural Resistance Responses**: Common objections and how to address them
- **Transition Guidance**: How to move naturally to the next category
- **Special Considerations**: Any unique aspects like skipping options or multiple identity management

## Context Key Details

**Key Name**: `brainstorming_category_context`  
**Enum Value**: `ContextKey.BRAINSTORMING_CATEGORY_CONTEXT`  
**Data Source**: `CoachState.identity_focus` (reads from markdown files)  
**Phase**: Identity Brainstorming (`IDENTITY_BRAINSTORMING`)

## Usage in Prompts

The context is automatically included when a prompt specifies the `brainstorming_category_context` key:

```python
prompt.required_context_keys = [
    ContextKey.USER_NAME,
    ContextKey.CURRENT_PHASE,
    ContextKey.BRAINSTORMING_CATEGORY_CONTEXT
]
```

## Benefits

### Targeted Guidance

- Provides category-specific examples and guidance
- Helps AI understand the current focus area
- Enables more relevant identity suggestions

### Consistent Experience

- Standardized category information across sessions
- Consistent guidance regardless of AI provider
- Maintains coaching process integrity

### Reduced Prompt Complexity

- Eliminates need to include all category information in every prompt
- Focuses AI attention on relevant category only
- Improves prompt performance and clarity
