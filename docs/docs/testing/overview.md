---
sidebar_position: 1
---

# Overview

The Test Scenario System is a comprehensive testing framework that allows administrators to create, manage, and simulate complete user coaching sessions. This system is essential for quality assurance, feature testing, and maintaining consistent testing environments.

## What is a Test Scenario?

A **test scenario** is a complete snapshot of a user's coaching session that includes:

- **User Profile**: Name, email, and basic information
- **Coach State**: Current coaching phase, identity focus, and progress
- **Identities**: All identities the user has created (career, health, relationships, etc.)
- **Chat History**: Complete conversation history with the Coach
- **User Notes**: Insights and observations captured during sessions
- **Actions**: System actions taken during the coaching process

Test scenarios are stored as JSON templates that can be instantiated to create actual database records for testing purposes.

## Key Benefits

### For Quality Assurance

- **Consistent Testing**: Every test starts from the same baseline state
- **Reproducible Results**: Tests can be run repeatedly with identical conditions
- **Isolated Data**: Test data is completely separate from production user data

### For Development

- **Feature Testing**: Test new features against realistic user states
- **Regression Testing**: Ensure changes don't break existing functionality
- **Performance Testing**: Measure system performance with realistic data loads

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
- **Coach State Visualization**: Real-time monitoring of test user states (see [Coach State Visualization](./coach-state-visualization) for details)

## Core Concepts

### Templates vs. Instances

- **Template**: The JSON definition of a scenario (stored in TestScenario model)
- **Instance**: The actual database records created from a template (User, CoachState, etc.)

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

## Permissions and Access

### Admin-Only Features

- Creating and editing test scenarios
- Accessing test scenario management interface
- Using freeze session functionality
- Resetting scenarios to template state

### Security Considerations

- Test scenarios are only accessible to admin users
- Test data is completely separate from production data
- All test scenario operations are logged for audit purposes

## Getting Started

To begin using the test scenario system:

1. **Access the Admin Interface**: Navigate to the test scenario management page
2. **Create Your First Scenario**: Use the scenario editor to define a test case
3. **Run the Scenario**: Start a test chat session with the scenario
4. **Monitor Results**: Use the coach state visualizer to track progress

For detailed instructions on each step, see:

- [Scenario Management](./scenario-management) - Creating and editing scenarios
- [Running Scenarios](./running-scenarios) - Using scenarios for testing
- [Freeze Session](./freeze-session) - Capturing live sessions as scenarios

## Related Documentation

- [Test Scenario API Reference](../api/endpoints/test-scenarios) - Backend API documentation
- [Test Scenario Database Model](../database/models/test-scenario) - Data model details
- [Coach State Visualization](./coach-state-visualization) - Real-time state monitoring
