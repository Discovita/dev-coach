---
sidebar_position: 2
---

# Test Scenario Management

This guide covers how to create, edit, and manage test scenarios using the admin interface. The scenario management system provides a comprehensive UI for defining complete user states for testing purposes.

## Accessing the Scenario Management Interface

1. **Navigate to Test Page**: Go to the `/test` route in the application
2. **Admin Permissions**: Ensure you have admin privileges (only admin users can access this interface)
3. **Scenario Table**: You'll see a table listing all existing test scenarios

![Test Scenario Management Interface - Shows the main table with scenario list and action buttons](/img/test-table.png)

_Figure 1: The main test scenario management interface showing the scenario table with available actions_ -->

## Creating a New Test Scenario

### Step 1: Open the Scenario Editor

1. **Click "+ New Scenario"**: Located in the page header next to "Test Scenarios"
2. **Editor Opens**: A modal dialog appears with the scenario editor interface

![New Scenario Button - Shows the + New Scenario button in the page header](/img/new-scenario-button.png)

_Figure 2: The + New Scenario button in the page header_ -->

### Step 2: Fill in General Information

The **General** tab contains basic scenario metadata:

- **Name**: Unique identifier for the scenario (required)
  - Use descriptive names like "Career Focus User - Mid Session"
  - Names must be unique across all scenarios
- **Description**: Optional description for documentation purposes
  - Explain the purpose or context of this scenario
  - Example: "User in career identity brainstorming phase with 2 identities created"

### Step 3: Define User Information

The **User** tab defines the test user's basic profile:

- **First Name**: User's first name (required)
- **Last Name**: User's last name (required)
- **Email**: Automatically generated (display only)
- **Password**: Automatically set to "Coach123!" (display only)

**Note**: Email and password are managed by the system and cannot be edited.

### Step 4: Configure Coach State

The **Coach State** tab defines the user's current coaching progress:

#### Required Fields

- **Current Phase**: Select from available coaching phases
  - `GET_TO_KNOW_YOU` - Initial assessment phase
  - `IDENTITY_BRAINSTORMING` - Creating initial identities
  - `IDENTITY_REFINEMENT` - Refining existing identities
  - `IDENTITY_AFFIRMATION` - Creating affirmations
  - `IDENTITY_VISUALIZATION` - Creating visualizations
  - `INTEGRATION_AND_APPLICATION` - Applying identities daily

#### Optional Fields

- **Identity Focus**: Primary identity category being worked on
- **Skipped Identity Categories**: Categories the user has chosen to skip
- **Who You Are**: Current self-perception statements
- **Who You Want to Be**: Aspirational identity statements
- **Asked Questions**: Questions already asked during the session
- **Current Identity**: Currently selected identity (if any)

### Step 5: Define Identities

The **Identities** tab allows you to create multiple identities for the test user:

#### Adding an Identity

1. **Click "Add Identity"**: Creates a new identity entry
2. **Fill Required Fields**:
   - **Name**: Identity name (e.g., "Career Professional")
   - **Category**: Identity category (Career, Health, Relationships, etc.)
3. **Fill Optional Fields**:
   - **Affirmation**: Positive statement about the identity
   - **Visualization**: Mental image or scenario for the identity
   - **Notes**: Additional observations or insights

#### Identity Categories

- **Career**: Professional and work-related identities
- **Health**: Physical and mental well-being identities
- **Relationships**: Family, friends, and romantic relationships
- **Spiritual**: Religious, philosophical, or meaning-based identities
- **Personal Appearance**: Self-image and presentation identities
- **Physical Expression**: Movement, sports, and physical activities
- **Familial Relations**: Family roles and responsibilities
- **Romantic Relations**: Dating and partnership identities
- **Doer of Things**: Action-oriented and achievement identities

### Step 6: Add Chat Messages

The **Chat Messages** tab defines the conversation history:

#### Adding Messages

1. **Click "Add Message"**: Creates a new message entry
2. **Select Role**:
   - **User**: Messages from the user
   - **Assistant**: Responses from the Coach
3. **Enter Content**: The actual message text
4. **Set Timestamp** (optional): When the message was sent

#### Message Structure

- Messages are displayed in chronological order
- Include realistic conversation flow
- Consider the coaching phase when writing messages
- Balance user input with Coach responses

### Step 7: Add User Notes

The **User Notes** tab captures insights and observations:

#### Adding Notes

1. **Click "Add Note"**: Creates a new note entry
2. **Enter Note Content**: The insight or observation
3. **Link to Source Message** (optional): Reference to specific chat message

#### Note Examples

- "User shows strong interest in career development"
- "User struggles with work-life balance"
- "User responds well to visualization exercises"

### Step 8: Define Actions

The **Actions** tab records system actions taken during the session:

#### Adding Actions

1. **Click "Add Action"**: Creates a new action entry
2. **Select Action Type**: Choose from available action types
3. **Set Parameters**: Action-specific parameters (JSON format)
4. **Add Result Summary** (optional): Description of action outcome
5. **Set Timestamp** (optional): When the action occurred

#### Common Action Types

- `CREATE_IDENTITY`: Creating a new identity
- `UPDATE_IDENTITY`: Modifying an existing identity
- `TRANSITION_PHASE`: Moving to a new coaching phase
- `SELECT_IDENTITY_FOCUS`: Setting the current focus identity
- `ADD_USER_NOTE`: Adding a user note

### Step 9: Save the Scenario

1. **Review All Tabs**: Ensure all required information is complete
2. **Click "Save"**: Creates the scenario and instantiates it
3. **Success Message**: Confirmation that the scenario was created
4. **Return to Table**: You'll be returned to the scenario list

<!-- ![Scenario Editor Save Button - Shows the Save button in the scenario editor](/img/scenario-editor-save.png)

*Figure 3: The Save button in the scenario editor* -->

## Editing Existing Scenarios

### Step 1: Access the Editor

1. **Find the Scenario**: Locate it in the scenario table
2. **Click "Edit"**: Opens the scenario editor with current data
3. **Review Current State**: All existing data is pre-populated

<!-- ![Edit Button - Shows the Edit button in the scenario table actions](/img/edit-button.png)

*Figure 4: The Edit button in the scenario table actions* -->

### Step 2: Make Changes

1. **Navigate Between Tabs**: Use the tab interface to access different sections
2. **Modify Fields**: Update any information as needed
3. **Add/Remove Items**: Add new entries or remove existing ones
4. **Validation**: Real-time validation ensures data integrity

### Step 3: Save Changes

1. **Click "Save"**: Updates the scenario and re-instantiates it
2. **Confirmation**: Success message confirms the update
3. **Data Refresh**: The scenario table updates with new information

## Deleting Scenarios

### Step 1: Initiate Deletion

1. **Find the Scenario**: Locate it in the scenario table
2. **Click "Delete"**: Opens a confirmation dialog
3. **Review Warning**: Dialog shows scenario name and deletion consequences

<!-- ![Delete Button - Shows the Delete button in the scenario table actions](/img/delete-button.png)

*Figure 5: The Delete button in the scenario table actions* -->

### Step 2: Confirm Deletion

1. **Read Warning**: Understand that deletion is permanent
2. **Review Scenario Details**: Dialog shows scenario name and description
3. **Click "Delete"**: Permanently removes the scenario
4. **Success Message**: Confirmation that deletion was successful

<!-- ![Delete Confirmation Dialog - Shows the delete confirmation dialog](/img/delete-confirmation-dialog.png)

*Figure 6: The delete confirmation dialog showing scenario details* -->

### Deletion Consequences

- **Template Removed**: The scenario template is permanently deleted
- **Test Data Cleaned**: All associated test user data is removed
- **No Recovery**: Deleted scenarios cannot be recovered
- **References Updated**: Any references to the deleted scenario are updated

## Template Validation

### Real-Time Validation

The scenario editor provides immediate feedback on data quality:

- **Required Fields**: Missing required fields are highlighted
- **Data Types**: Invalid data types show error messages
- **Format Validation**: Email addresses, timestamps, and other formats are validated
- **Relationship Validation**: References between sections are checked

### Common Validation Errors

- **Missing Required Fields**: Name, first name, last name, etc.
- **Invalid Email Format**: Email addresses must be valid format
- **Invalid Timestamps**: Timestamps must be in ISO format
- **Invalid Action Parameters**: Action parameters must be valid JSON
- **Duplicate Names**: Scenario names must be unique

### Error Resolution

1. **Read Error Message**: Understand what needs to be fixed
2. **Navigate to Tab**: Go to the relevant tab section
3. **Fix the Issue**: Correct the data according to the error message
4. **Re-validate**: Errors clear automatically when fixed

## Best Practices

### Scenario Naming

- Use descriptive, unique names
- Include the coaching phase in the name
- Add context about the scenario purpose
- Examples: "Career Focus - Mid Brainstorming", "Health Identity - Ready for Affirmation"

### Template Organization

- Start with simple scenarios and add complexity
- Include realistic conversation flows
- Balance user input with Coach responses
- Consider the coaching phase when designing scenarios

### Data Quality

- Use realistic names and email addresses
- Include complete conversation histories
- Add meaningful user notes and insights
- Ensure actions match the conversation flow

### Maintenance

- Regularly review and update scenarios
- Delete outdated or unused scenarios
- Document scenario purposes in descriptions
- Test scenarios periodically to ensure they work correctly

## Related Documentation

- [Running Scenarios](./running-scenarios) - How to use scenarios for testing
- [Freeze Session](./freeze-session) - Capturing live sessions as scenarios
- [Test Scenario API Reference](../api/endpoints/test-scenarios) - Backend API details
- [Coach State Visualization](./coach-state-visualization) - Monitoring scenario state
