---
sidebar_position: 1
---

# Prompt Manager System

The Prompt Manager is a core component of the Dev Coach system that handles the construction and management of AI prompts used during coaching sessions.

## Overview

The Prompt Manager is responsible for:
- Storing prompt templates in the database
- Constructing dynamic prompts based on user context
- Managing different prompt versions for different coaching phases
- Providing context keys and allowed actions for each prompt

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Message  │    │  Prompt Manager │    │   AI Service    │
│                 │───►│                 │───►│                 │
│  - Current      │    │  - Template     │    │  - OpenAI       │
│    Phase        │    │    Selection    │    │  - Anthropic    │
│  - User Data    │    │  - Context      │    │  - Response     │
│  - Chat History │    │    Assembly     │    │  - Actions      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Key Components

### 1. Prompt Templates
Stored in the database with the following structure:
- **Template ID**: Unique identifier for the prompt
- **Coaching Phase**: Which phase this prompt is used for
- **Template Text**: The actual prompt template with placeholders
- **Context Keys**: What data should be included in the prompt
- **Allowed Actions**: What actions the AI can perform
- **Version**: Version number for prompt iteration

### 2. Context Keys
Define what information should be included in the prompt:
- **User Data**: Basic user information
- **Coach State**: Current coaching phase and progress
- **Identities**: User's created identities
- **Chat History**: Recent conversation context
- **System Data**: Technical information and settings

### 3. Allowed Actions
Specify what actions the AI can perform:
- **Create Identity**: Create a new identity for the user
- **Update Identity**: Modify an existing identity
- **Transition Phase**: Move to a different coaching phase
- **Set Goals**: Establish goals for an identity
- **Track Progress**: Record progress on goals

## Prompt Construction Process

1. **Phase Detection**: Determine current coaching phase
2. **Template Selection**: Find appropriate prompt template
3. **Context Assembly**: Gather all required context data
4. **Template Rendering**: Fill in template placeholders
5. **Action Instructions**: Add allowed action instructions
6. **Final Prompt**: Deliver complete prompt to AI service

## Database Schema

### Prompts Table
```sql
CREATE TABLE prompts (
    id SERIAL PRIMARY KEY,
    coaching_phase VARCHAR(50) NOT NULL,
    template_text TEXT NOT NULL,
    context_keys JSONB,
    allowed_actions JSONB,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Context Keys
```json
{
    "user_data": ["name", "email", "preferences"],
    "coach_state": ["current_phase", "progress", "goals"],
    "identities": ["all_identities", "active_identity"],
    "chat_history": ["recent_messages", "conversation_context"],
    "system_data": ["ai_provider", "model_version"]
}
```

## Example Prompt Template

```markdown
You are a life coach helping {{user.name}} through their coaching journey.

Current Phase: {{coach_state.current_phase}}
Progress: {{coach_state.progress}}

User's Identities:
{% for identity in identities %}
- {{identity.name}}: {{identity.description}}
{% endfor %}

Recent Conversation:
{{chat_history.recent_messages}}

Your task is to help {{user.name}} with {{coach_state.current_phase}}.

Allowed Actions:
- create_identity: Create a new identity
- update_identity: Update an existing identity
- transition_phase: Move to next phase
- set_goals: Set goals for an identity

Please respond naturally and use the allowed actions as needed.
```

## Version Management

The Prompt Manager supports versioning to allow for:
- **A/B Testing**: Test different prompt versions
- **Iterative Improvement**: Gradually improve prompts
- **Rollback Capability**: Revert to previous versions if needed
- **Development Workflow**: Safe testing of new prompts

## Integration Points

### With Action Handler
- Provides allowed actions list
- Receives action execution results
- Updates context based on actions taken

### With Coach State
- Reads current phase and progress
- Updates state based on AI responses
- Maintains conversation context

### With AI Services
- Sends constructed prompts
- Receives AI responses
- Handles different AI provider formats

## Best Practices

### Prompt Design
1. **Clear Instructions**: Be explicit about what the AI should do
2. **Context Relevance**: Include only relevant context
3. **Action Clarity**: Clearly define allowed actions
4. **Natural Language**: Use conversational, coaching-appropriate language

### Version Control
1. **Incremental Changes**: Make small, testable changes
2. **Documentation**: Document what each version changes
3. **Testing**: Test new versions before deployment
4. **Monitoring**: Track performance of different versions

### Performance
1. **Context Optimization**: Include only necessary context
2. **Template Efficiency**: Use efficient template rendering
3. **Caching**: Cache frequently used prompts
4. **Database Indexing**: Optimize database queries

## Troubleshooting

### Common Issues
1. **Missing Context**: Ensure all required context keys are available
2. **Invalid Actions**: Verify allowed actions are properly formatted
3. **Template Errors**: Check template syntax and placeholders
4. **Version Conflicts**: Ensure correct prompt version is being used

### Debugging
1. **Log Prompt Construction**: Log the final prompt for debugging
2. **Context Validation**: Validate context data before prompt construction
3. **Action Validation**: Verify action format before sending to AI
4. **Performance Monitoring**: Track prompt construction time

---

Next, learn about the [Action Handler System](./action-handler.md) or explore [Coach Phases](./coach-phases.md).
