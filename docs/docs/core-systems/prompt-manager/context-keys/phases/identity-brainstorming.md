---
sidebar_position: 1
---

# Identity Brainstorming Context

The `brainstorming_category_context` context key provides phase-specific information during the Identity Brainstorming coaching phase. This context helps the AI understand what category of identities the user is currently working on and provides relevant guidance.

## Context Key Details

**Key Name**: `brainstorming_category_context`  
**Enum Value**: `ContextKey.BRAINSTORMING_CATEGORY_CONTEXT`  
**Data Source**: `CoachState.brainstorming_category_context`  
**Phase**: Identity Brainstorming (`IDENTITY_BRAINSTORMING`)

## What Data It Provides

The brainstorming category context contains information about:
- The current identity category being brainstormed
- Category-specific guidance and examples
- Progress within the current category
- Available identity categories

## Example Context Data

```python
# Example context data for "Career" category
brainstorming_category_context = """
Current Category: Career

Available Career Identity Categories:
- Professional Role (e.g., "Innovative Software Engineer")
- Industry Expert (e.g., "AI Ethics Thought Leader") 
- Leadership Position (e.g., "Empathetic Team Manager")
- Creative Professional (e.g., "Strategic Design Thinker")
- Entrepreneurial (e.g., "Sustainable Business Builder")

Focus Areas for Career Identities:
- Skills and expertise
- Professional values and principles
- Impact and contribution
- Growth and development
- Work-life integration

Current Progress: 2 of 5 career identities completed
"""
```

## Implementation

### Context Function

```python
def get_brainstorming_category_context(coach_state: CoachState) -> str:
    """Get context for identity brainstorming based on current category."""
    if not coach_state.brainstorming_category_context:
        return "No specific category context available."
    
    return coach_state.brainstorming_category_context
```

### Database Storage

The context is stored in the `CoachState` model:

```python
class CoachState(models.Model):
    # ... other fields
    brainstorming_category_context = models.TextField(
        blank=True, 
        null=True,
        help_text="Context for identity brainstorming category"
    )
```

## Category-Specific Context

Different identity categories provide different context:

### Career Category
- Professional roles and responsibilities
- Industry-specific terminology
- Career progression paths
- Professional development focus

### Health Category
- Physical and mental wellness
- Lifestyle and habits
- Health goals and aspirations
- Wellness practices and routines

### Relationships Category
- Family and social connections
- Communication styles
- Relationship dynamics
- Personal boundaries and values

### Personal Growth Category
- Learning and development
- Personal values and beliefs
- Life purpose and meaning
- Self-improvement goals

### Financial Category
- Financial goals and values
- Money mindset and beliefs
- Financial planning and security
- Wealth building strategies

## Usage in Prompts

### Template Example

```markdown
You are helping {{user_name}} brainstorm identities in the {{current_phase}} phase.

{{brainstorming_category_context}}

Based on this context, help them explore potential identities that align with their values and goals.
```

### Prompt Integration

The context is automatically included when a prompt specifies the `brainstorming_category_context` key:

```python
prompt.required_context_keys = [
    ContextKey.USER_NAME,
    ContextKey.CURRENT_PHASE,
    ContextKey.BRAINSTORMING_CATEGORY_CONTEXT
]
```

## Dynamic Updates

The brainstorming category context is updated as the user progresses:

1. **Category Selection**: When user chooses a category to focus on
2. **Progress Tracking**: As identities are created within the category
3. **Category Completion**: When moving to the next category
4. **Context Refinement**: Based on user feedback and preferences

## Benefits

### Targeted Guidance
- Provides category-specific examples and guidance
- Helps AI understand the current focus area
- Enables more relevant identity suggestions

### Progress Tracking
- Shows completion status within categories
- Helps maintain momentum and focus
- Provides context for next steps

### Consistent Experience
- Standardized category information across sessions
- Consistent guidance regardless of AI provider
- Maintains coaching process integrity

## Related Context Keys

- `current_phase`: Confirms the user is in the brainstorming phase
- `identities`: Shows existing identities for context
- `number_of_identities`: Indicates progress
- `user_notes`: May contain category preferences

## Error Handling

- **Missing Context**: Returns default message if no category context is set
- **Invalid Category**: Validates category against available options
- **Empty Context**: Handles cases where context field is empty

## Future Enhancements

Potential improvements to the brainstorming context:
- Category-specific success stories and examples
- Personalized category recommendations
- Integration with user preferences and history
- Dynamic category suggestions based on progress
