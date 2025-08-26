---
sidebar_position: 2
---

# Test Scenario Management

This guide covers the three main operations for managing test scenarios: starting/freezing scenarios, editing scenarios, and deleting scenarios.

## Starting and Freezing Test Scenarios

### Starting a Test Scenario

As covered in the [Overview](./overview), clicking "Start" on any test scenario will:

1. Load the existing database records created from the scenario template
2. Allow you to pick up where you left off if you've previously worked with this scenario
3. Let you interact with the Coach normally, with all actions, notes, and messages being saved

![Start Button Highlighted - Shows the Start button highlighted in the scenario table actions](/img/test-scenario-table-start-button-highlighted.png)

_Figure 3: The Start button highlighted in the scenario table actions_

### Freezing a Test Scenario

The recommended way to create test scenarios is by "freezing" an existing coaching session:

1. **Navigate to the Test Page**: Access the `/test` route as an admin user
2. **Use Freeze Session**: This captures the current state of any user's coaching session
3. **Complete Snapshot**: All database items (user data, coach state, identities, chat messages, user notes, actions) are replicated into the scenario template
4. **Template Creation**: A new test scenario is created with the frozen session data

This approach ensures all the complex relationships between different parts of the coaching session are correctly captured and maintained.

![Create Test Scenario Button - Shows the + New Scenario button in the page header](/img/create-test-scenario-button.png)

_Figure 1: The + New Scenario button for creating test scenarios_

## Editing Test Scenarios

### Accessing the Edit Form

1. **Find the Scenario**: Locate it in the test scenario table
2. **Click "Edit"**: Opens the test scenario edit form with all current data

![Edit Test Scenario Form - Shows the edit form with multiple tabs for editing scenario data](/img/edit-test-scenario-form.png)

_Figure 2: The edit form with multiple tabs for editing scenario data_

### Edit Form Structure

The edit form has multiple tabs that allow you to update everything associated with the test scenario:

#### General Information
- **Title**: Update the scenario name
- **Description**: Modify the scenario description for tracking purposes

#### Data Sections
- **User**: Edit user profile information
- **Coach State**: Modify coaching phase, identity focus, and progress data
- **Identities**: Update, add, or remove user identities
- **Chat Messages**: Edit conversation history
- **User Notes**: Modify insights and observations
- **Actions**: Update system actions taken during the session

**Important**: When editing chat messages, ensure the last message in the conversation history is from the Coach (Assistant role). If the last message is from the User, you'll end up with two consecutive User messages when you continue the conversation, which can cause issues with the Coach's response flow.

### Saving Changes

When you click "Save" after editing:

1. **Template Update**: The scenario template in the database is updated with your changes
2. **Reset Execution**: The system automatically calls the reset API endpoint
3. **Fresh Instance**: All database records are recreated from the updated template
4. **Clean State**: The scenario returns to the exact state defined in your edited template

This ensures that any changes you make to the scenario are immediately reflected in a clean, fresh instance.

## Deleting Test Scenarios

### Delete Process

1. **Click "Delete"**: Located in the scenario table actions
2. **Confirmation Modal**: A dialog appears asking "Are you sure you want to delete this?"
3. **Confirm Deletion**: Click to proceed with deletion

### What Gets Deleted

- **Test Scenario Template**: The scenario definition is permanently removed from the database
- **User Information**: All associated test user data is deleted
- **Related Records**: Coach state, identities, chat messages, user notes, and actions are all removed

**Warning**: Deletion is permanent and cannot be undone.

## Related Documentation

- [Overview](./overview) - Understanding test scenarios and the development workflow
- [Running Scenarios](./running-scenarios) - How to use scenarios for testing
- [Test Scenario API Reference](../api/endpoints/test-scenarios) - Backend API details
