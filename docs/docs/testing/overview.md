---
sidebar_position: 1
---

# Overview

The Test Scenario System allows administrators to create, manage, and simulate complete user coaching sessions for development and testing purposes.

## What is a Test Scenario?

A **test scenario** is a complete snapshot of a user's coaching session that includes:

- **User Profile**: Name, email, and basic information
- **Coach State**: Current coaching phase, identity focus, and progress
- **Identities**: All identities the user has created (career, health, relationships, etc.)
- **Chat History**: Complete conversation history with the Coach
- **User Notes**: Insights and observations captured during sessions
- **Actions**: System actions taken during the coaching process

Test scenarios are stored as JSON templates that can be instantiated to create actual database records for testing purposes.

## System Architecture

### Backend Components

#### TestScenario Model

- Stores scenario templates as JSON data
- Includes metadata (name, description, creation info)
- Links to creator for audit purposes

#### Template Structure

Each scenario template contains sections for different aspects of a user's state:

```json
{
  "user": { "first_name": "John", "last_name": "Doe", "email": "john@example.com" },
  "coach_state": { "current_phase": "IDENTITY_BRAINSTORMING", "identity_focus": "CAREER" },
  "identities": [
    { "name": "Career Professional", "category": "CAREER", "affirmation": "I am..." }
  ],
  "chat_messages": [
    { "role": "user", "content": "I want to improve my career" },
    { "role": "assistant", "content": "Let's explore your career identity..." }
  ],
  "user_notes": [
    { "note": "User shows strong interest in career development" }
  ],
  "actions": [
    { "action_type": "CREATE_IDENTITY", "parameters": {...} }
  ]
}
```

#### API Endpoints

See [Test Scenarios API Reference](../api/endpoints/test-scenarios) for complete endpoint documentation including:

- **CRUD Operations**: Create, read, update, delete scenarios
- **Reset Functionality**: Reset scenarios to their original template state
- **Freeze Session**: Capture live user sessions as new scenarios

### Frontend Components

#### Admin Management Interface

- **Scenario Table**: List and manage all test scenarios
- **Scenario Editor**: Create and edit scenario templates
- **Test Chat Interface**: Simulate coaching sessions with test users

#### Key Features

- **Template Validation**: Real-time validation of scenario templates
- **Optimistic UI**: Instant feedback for user actions
- **Coach State Visualization**: Real-time monitoring of test user states

## Core Concepts

### Scenario Lifecycle

1. **Creation**: Define scenario template with desired user state
2. **Instantiation**: Create actual database records from template
3. **Testing**: Use the instantiated scenario for testing
4. **Reset**: Return scenario to original template state
5. **Modification**: Update template and re-instantiate

### Data Isolation

- All test scenario data is clearly marked and isolated
- Test users have distinct email addresses and IDs
- Easy cleanup and maintenance of test data

## Admin Session Management

### Test Scenarios vs. Personal Sessions

As an admin, you have access to both test scenarios and your personal coaching session. The system maintains a clear distinction between these:

- **Test Scenarios**: Predefined templates that create isolated test environments
- **Personal Session**: Your own coaching session that persists across admin activities

![Resume My Session Button - Shows the Resume My Session button at the bottom of the page](/img/resume-my-session-button.png)

_Figure 2: The Resume My Session button for continuing your own coaching session_

### Working with Test Scenarios

When you click "Start" on any test scenario:

1. **Session Initiation**: The system loads the existing database records that were created from the scenario template
2. **Session Continuity**: If you or anyone else has previously worked with this scenario, you'll pick up where you left off.
3. **Normal App Behavior**: The Coach works exactly as it would for regular users - saving actions, user notes, chat messages, etc.
4. **Data Accumulation**: All new interactions are stored "on top of" the original template

### Resetting Test Scenarios

While in a test scenario chat session, you can click "Reset Test Conversation" to:

- **Complete Reset**: Cascade delete ALL records associated with the test user
- **Fresh Start**: Recreate all database records according to the original template
- **Template Restoration**: Return to the exact state defined in the scenario template

**Note**: The current implementation uses a full delete-and-recreate approach rather than more efficient delta updates. While not optimal, this approach is acceptable for the current admin-only functionality.

## Development and Iteration Workflow

### Rapid Prompt Testing

The test scenario system is particularly valuable for development and prompt iteration:

1. **Create a Test Scenario**: Set up a scenario that represents a specific coaching situation
2. **Test Prompt Changes**: Modify prompts for a coaching phase and test them immediately
3. **Iterate Quickly**: If the Coach's behavior isn't what you want, tweak the prompt and reset the scenario
4. **Repeat**: Test the updated prompt with the same baseline scenario

This workflow allows you to:
- **Isolate Prompt Changes**: Test only the prompt modifications without other variables
- **Maintain Consistency**: Use the same test scenario to compare different prompt versions
- **Speed Up Development**: Quickly iterate on coaching logic without affecting real users

> ⚠️ **Note**: There is an ongoing issue with OpenAI's prompt caching that may affect rapid iteration. OpenAI might cache responses for similar prompts, leading to the same response even after changes. This can give the impression that prompt modifications are ineffective. Potential solutions for this caching behavior are currently under investigation.

### Best Practices for Prompt Iteration

- **Document Changes**: Keep track of what changes you're testing
- **Use Distinct Scenarios**: Create different test scenarios for different coaching situations
- **Test Multiple Interactions**: Don't just test the first response - continue the conversation to see how the prompt performs
- **Reset Frequently**: Use the reset functionality to ensure you're testing with a clean slate

## Getting Started

To begin using the test scenario system:

1. **Access the Admin Interface**: Navigate to the test scenario management page
2. **Create Your First Scenario**: Use the scenario editor to define a test case
3. **Run the Scenario**: Start a test chat session with the scenario
4. **Monitor Results**: Use the coach state visualizer to track progress

![Test Scenario Management Interface - Shows the main table with scenario list and action buttons](/img/test-scenario-table.png)

_Figure 1: The main test scenario management interface showing the scenario table with available actions_

For detailed instructions on each step, see:

- [Scenario Management](./scenario-management) - Creating and editing scenarios
- [Running Scenarios](./running-scenarios) - Using scenarios for testing
- [Freeze Session](./freeze-session) - Capturing live sessions as scenarios

## Related Documentation

- [Test Scenario API Reference](../api/endpoints/test-scenarios) - Backend API documentation
- [Test Scenario Database Model](../database/models/test-scenario) - Data model details
- [Coach State Visualization](./coach-state-visualization) - Real-time state monitoring
