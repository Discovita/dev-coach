---
sidebar_position: 4
---

# Freeze Session Feature

The Freeze Session feature allows administrators to capture the current state of any user session and create a new test scenario from it. This powerful tool enables you to quickly create realistic test scenarios from actual user interactions.

## What is Freeze Session?

**Freeze Session** captures a complete snapshot of a user's coaching session, including:

- **User Profile**: Name, email, and basic information
- **Coach State**: Current coaching phase, identity focus, and progress
- **Identities**: All identities the user has created
- **Chat History**: Complete conversation history
- **User Notes**: Insights and observations captured during sessions
- **Actions**: System actions taken during the coaching process

The captured data is automatically converted into a valid test scenario template that can be used for testing and quality assurance.

## When to Use Freeze Session

### Ideal Use Cases

#### Quality Assurance
- **Capture Bug Scenarios**: Freeze sessions where issues occur
- **Regression Testing**: Preserve problematic user states
- **Feature Testing**: Capture realistic user interactions for testing

#### Development
- **Demo Scenarios**: Create scenarios for demonstrations
- **Training Examples**: Capture good examples for training
- **Edge Cases**: Preserve unusual but valid user states

#### User Research
- **Interesting Conversations**: Capture particularly good coaching sessions
- **User Patterns**: Document common user behaviors
- **Success Stories**: Preserve successful coaching outcomes

### When NOT to Use Freeze Session

- **Personal Information**: Avoid freezing sessions with sensitive personal data
- **Incomplete Sessions**: Don't freeze sessions that are clearly incomplete
- **Error States**: Avoid freezing sessions with system errors
- **Test Data**: Don't freeze sessions that are already test scenarios

## Accessing the Freeze Session Feature

### From Test Chat Interface

#### For Test Scenario Sessions
1. **Start a Test Scenario**: Begin a test scenario session
2. **Interact with the Scenario**: Have conversations and make changes
3. **Click "Freeze Session"**: Located in the chat interface
4. **Fill in Details**: Provide scenario name and description
5. **Create Scenario**: Confirm to create the new scenario

#### For Admin Sessions
1. **Resume Your Session**: Click "Resume My Session" on the test page
2. **Have Conversations**: Interact with the Coach normally
3. **Click "Freeze Session"**: Located in the chat interface
4. **Fill in Details**: Provide scenario name and description
5. **Create Scenario**: Confirm to create the new scenario

### From Scenario Management

The freeze session feature is also available from the main scenario management interface for capturing admin sessions.

## Freeze Session Process

### Step 1: Prepare the Session

Before freezing a session, ensure it's in a good state:

1. **Complete Conversations**: Finish any ongoing conversations
2. **Verify State**: Check that the coach state is accurate
3. **Review Identities**: Ensure identities are properly created
4. **Check Notes**: Verify user notes are meaningful

### Step 2: Initiate Freeze

1. **Click "Freeze Session"**: Located in the chat interface
2. **Modal Opens**: Freeze session dialog appears
3. **Review Information**: Check the session details displayed

### Step 3: Provide Scenario Details

#### Required Information
- **Scenario Name**: Unique name for the new scenario
  - Use descriptive names like "Career Focus - Mid Brainstorming"
  - Include context about the session state
  - Names must be unique across all scenarios

#### Optional Information
- **Description**: Detailed explanation of the scenario
  - Explain what makes this session interesting or useful
  - Include the coaching phase and key characteristics
  - Example: "User in career identity brainstorming phase, shows strong engagement and has created 2 identities"

#### User Name Override
- **First Name**: Override the user's first name (optional)
- **Last Name**: Override the user's last name (optional)
- **Defaults**: If not provided, uses the actual user names or defaults to "Test User"

### Step 4: Create the Scenario

1. **Review Details**: Double-check the scenario information
2. **Click "Create Scenario"**: Confirms the freeze operation
3. **Wait for Processing**: System captures and processes the data
4. **Success Confirmation**: New scenario is created successfully

## What Gets Captured

### User Data
- **Profile Information**: First name, last name, email
- **Account Details**: User ID and basic account information

### Coach State
- **Current Phase**: Active coaching phase
- **Identity Focus**: Current focus identity category
- **Skipped Categories**: Identity categories the user skipped
- **Who You Are**: Current self-perception statements
- **Who You Want to Be**: Aspirational identity statements
- **Asked Questions**: Questions already asked during the session
- **Current Identity**: Currently selected identity (if any)

### Identities
- **All Created Identities**: Complete identity information
- **Identity Names**: Names given to each identity
- **Categories**: Identity categories (Career, Health, etc.)
- **States**: Current state of each identity
- **Affirmations**: Affirmations created for identities
- **Visualizations**: Visualizations created for identities
- **Notes**: Any notes associated with identities

### Chat Messages
- **Complete History**: All messages in chronological order
- **User Messages**: Everything the user has said
- **Coach Responses**: All responses from the Coach
- **Timestamps**: When each message was sent

### User Notes
- **All Notes**: Insights and observations captured
- **Note Content**: The actual note text
- **Source Messages**: Links to related chat messages
- **Creation Times**: When notes were created

### Actions
- **System Actions**: All actions taken by the system
- **Action Types**: Types of actions (CREATE_IDENTITY, etc.)
- **Parameters**: Action-specific parameters
- **Results**: Action outcomes and summaries
- **Timestamps**: When actions occurred

## Template Generation

### Automatic Processing

The freeze session feature automatically:

1. **Gathers Data**: Collects all relevant user data
2. **Validates Structure**: Ensures data meets template requirements
3. **Formats Template**: Converts data to proper JSON template format
4. **Creates Scenario**: Saves the new test scenario
5. **Instantiates Data**: Creates actual database records for the scenario

### Template Validation

The system validates the captured data against the template schema:

- **Required Fields**: Ensures all required fields are present
- **Data Types**: Validates data types and formats
- **Relationships**: Checks relationships between different sections
- **Consistency**: Ensures data consistency across sections

### Error Handling

If validation fails:

- **Error Display**: Shows specific validation errors
- **Data Review**: Allows review of problematic data
- **Manual Correction**: Option to manually fix issues
- **Retry**: Ability to retry the freeze operation

## Best Practices

### Session Preparation

#### Before Freezing
- **Complete Conversations**: Finish any ongoing discussions
- **Verify State**: Ensure coach state is accurate
- **Review Data**: Check that all data looks correct
- **Test Functionality**: Verify the session works as expected

#### During Freezing
- **Use Descriptive Names**: Choose clear, meaningful scenario names
- **Add Good Descriptions**: Explain what makes the session valuable
- **Consider Privacy**: Avoid capturing sensitive personal information
- **Document Context**: Include relevant context in descriptions

### Naming Conventions

#### Scenario Names
- **Include Phase**: Mention the coaching phase
- **Add Context**: Include key characteristics
- **Use Descriptors**: Add descriptive terms
- **Examples**:
  - "Career Focus - Mid Brainstorming"
  - "Health Identity - Ready for Affirmation"
  - "Multi-Identity User - Complex Session"

#### Descriptions
- **Explain Purpose**: Why this session is useful
- **Include Details**: Key characteristics and state
- **Mention Phase**: Current coaching phase
- **Note Identities**: Number and types of identities

### Data Quality

#### What to Capture
- **Interesting Sessions**: Sessions with good coaching interactions
- **Edge Cases**: Unusual but valid user states
- **Success Stories**: Sessions showing good outcomes
- **Problem Scenarios**: Sessions where issues occurred

#### What to Avoid
- **Incomplete Sessions**: Sessions that are clearly unfinished
- **Error States**: Sessions with system errors
- **Sensitive Data**: Sessions with personal information
- **Test Data**: Sessions that are already test scenarios

## Troubleshooting

### Common Issues

#### Freeze Session Button Not Visible
- **Check Permissions**: Ensure you have admin access
- **Verify Session**: Make sure you're in a valid session
- **Refresh Interface**: Try refreshing the page
- **Check Location**: Ensure you're in the correct interface

#### Validation Errors
- **Review Data**: Check the captured data for issues
- **Fix Problems**: Correct any data problems
- **Retry Operation**: Try the freeze operation again
- **Manual Creation**: Consider creating scenario manually

#### Processing Failures
- **Check Network**: Ensure stable internet connection
- **Try Again**: Retry the freeze operation
- **Contact Support**: Report persistent issues
- **Manual Backup**: Consider manually documenting the session

### Error Messages

#### "User not found"
- **Check User ID**: Verify the user exists
- **Refresh Session**: Try refreshing the session
- **Restart Session**: Start a new session

#### "Scenario name already exists"
- **Choose Different Name**: Use a unique scenario name
- **Check Existing**: Review existing scenario names
- **Add Suffix**: Add date or version to the name

#### "Invalid template data"
- **Review Data**: Check the captured data structure
- **Fix Issues**: Correct any data problems
- **Try Again**: Retry the freeze operation

## Related Documentation

- [Scenario Management](./scenario-management) - Creating and editing scenarios manually
- [Running Scenarios](./running-scenarios) - Using scenarios for testing
- [Test Scenario API Reference](../api/endpoints/test-scenarios) - Backend API details
- [Coach State Visualization](./coach-state-visualization) - Understanding session state
