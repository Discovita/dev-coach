---
sidebar_position: 3
---

# Running Test Scenarios

This guide explains how to run test scenarios to simulate coaching sessions and test system functionality. The test scenario system provides a complete chat interface that mimics real user interactions.

## Accessing the Test Interface

### Step 1: Navigate to Test Page

1. **Go to Test Route**: Navigate to `/test` in the application
2. **Admin Access**: Ensure you have admin privileges
3. **Scenario Table**: View all available test scenarios

### Step 2: Choose a Scenario or Resume Your Session

You have two main options:

#### Option A: Use a Test Scenario
Choose from the available test scenarios in the table.

#### Option B: Resume Your Own Session
Click the "Resume My Session" button at the bottom of the page to continue your own coaching session.

<!-- ![Resume My Session Button - Shows the Resume My Session button at the bottom of the page](/img/resume-my-session-button.png)

*Figure 1: The Resume My Session button for continuing your own coaching session* -->

The scenario table displays:
- **Name**: Descriptive name of the test scenario
- **Description**: Brief explanation of the scenario
- **Actions**: Start, Edit, Delete buttons for each scenario

<!-- ![Scenario Table Actions - Shows the action buttons for each scenario](/img/scenario-table-actions.png)

*Figure 2: The action buttons (Start, Edit, Delete) for each scenario in the table* -->

## Starting a Test Scenario

### Option 1: Continue from Current State

**Use this option when you want to:**
- Continue testing from where the scenario left off
- Preserve any changes made during previous test sessions
- Test incremental features or changes

**Steps:**
1. **Find the Scenario**: Locate the desired scenario in the table
2. **Click "Start"**: Begins the test session with current state
3. **Chat Interface Opens**: Full chat interface loads with test user data

<!-- ![Start Button - Shows the Start button in the scenario table actions](/img/start-button.png)

*Figure 3: The Start button to begin a test scenario session* -->

### Option 2: Start Fresh (Reset to Template)

**Use this option when you want to:**
- Start with a clean, known state
- Test the complete scenario from beginning
- Ensure consistent baseline for testing

**Steps:**
1. **Find the Scenario**: Locate the desired scenario in the table
2. **Click "Start"**: Begins the test session with current state
3. **Reset from Chat Interface**: Use the reset button in the chat interface to reset to template state
4. **Chat Interface Opens**: Full chat interface loads with test user data

**Note**: The reset functionality is available within the chat interface, not from the main table.

## Test Chat Interface

### Interface Layout

The test chat interface provides a complete coaching simulation:

<!-- ![Test Chat Interface Layout - Shows the complete test chat interface with chat area and visualizer](/img/test-chat-interface.png)

*Figure 6: The complete test chat interface showing chat area and coach state visualizer* -->

#### Header Section
- **Test Mode Indicator**: Shows "Test Mode: [Scenario Name]"
- **Back to Test Selection Button**: Returns to scenario selection

#### Main Chat Area
- **Chat Messages**: Complete conversation history
- **Message Input**: Send new messages as the test user
- **Send Button**: Submit messages to the Coach

#### Coach State Visualizer (Right Panel)
- **Real-time State**: Current coaching phase and progress
- **Identities**: All user identities with details
- **Chat History**: Complete message history
- **User Notes**: Insights and observations

*Note: For detailed information about the Coach State Visualizer, see [Coach State Visualization](./coach-state-visualization).*

### Using the Chat Interface

#### Sending Messages
1. **Type Message**: Enter your message in the input field
2. **Click Send**: Submit the message to the Coach
3. **View Response**: Coach responds based on current state
4. **Continue Conversation**: Build on the conversation naturally

#### Message Guidelines
- **Be Realistic**: Write messages as a real user would
- **Follow Context**: Consider the current coaching phase
- **Ask Questions**: Test the Coach's ability to guide users
- **Express Concerns**: Test how the Coach handles challenges

#### Example Conversation Flow
```
User: "I'm feeling overwhelmed with my career goals"
Coach: "I understand that feeling. Let's explore what's causing this overwhelm..."

User: "I want to be more confident at work"
Coach: "Confidence is a great goal. Let's work on your career identity..."
```

### Monitoring Test Progress

#### Coach State Visualizer
The right panel provides real-time monitoring:

- **Current Phase**: Shows the active coaching phase
- **Identity Focus**: Displays the current focus area
- **Identities List**: All created identities with details
- **Progress Indicators**: Visual representation of completion

#### Key Metrics to Monitor
- **Phase Transitions**: When and how phases change
- **Identity Creation**: New identities being created
- **User Engagement**: Quality of user responses
- **System Actions**: Actions triggered by conversations

## Resetting Scenarios

### When to Reset

**Reset scenarios when:**
- Testing is complete and you want a clean state
- Scenario has become inconsistent or corrupted
- Starting a new round of testing
- Preparing for demonstrations

### Reset Process

#### From Chat Interface
1. **Click Reset Button**: Located in the chat interface
2. **Confirm Reset**: Dialog asks for confirmation
3. **Wait for Completion**: System resets all data
4. **Fresh Start**: Scenario returns to template state

<!-- ![Reset Button - Shows the reset button in the chat interface](/img/reset-button.png)

*Figure 5: The reset button in the test chat interface* -->

### Reset Consequences

**What Gets Reset:**
- All chat messages return to template state
- Coach state reverts to template configuration
- Identities return to original template
- User notes reset to template values
- Actions reset to template state

**What Stays the Same:**
- Scenario template remains unchanged
- Scenario metadata (name, description) unchanged
- Test user profile unchanged

## Testing Different Scenarios

### Scenario Types

#### Phase-Specific Scenarios
- **Get to Know You**: Test initial assessment phase
- **Identity Brainstorming**: Test identity creation
- **Identity Refinement**: Test identity development
- **Affirmation Phase**: Test affirmation creation
- **Visualization Phase**: Test visualization exercises
- **Integration Phase**: Test daily application

#### Edge Case Scenarios
- **Multiple Identities**: Test with many identities
- **Skipped Categories**: Test with skipped identity categories
- **Complex Conversations**: Test with detailed user responses
- **Error Conditions**: Test error handling and recovery

### Testing Strategies

#### Functional Testing
1. **Feature Testing**: Test specific features or changes
2. **Regression Testing**: Ensure existing functionality works
3. **Integration Testing**: Test how components work together
4. **Performance Testing**: Test with realistic data loads

#### User Experience Testing
1. **Conversation Flow**: Test natural conversation progression
2. **Response Quality**: Evaluate Coach response quality
3. **Phase Transitions**: Test smooth phase transitions
4. **Error Handling**: Test how system handles errors

#### Scenario-Specific Testing
1. **Template Validation**: Ensure scenarios work correctly
2. **Data Consistency**: Verify data integrity
3. **State Management**: Test state transitions
4. **Action Execution**: Verify system actions work

## Best Practices for Running Scenarios

### Preparation
- **Review Scenario**: Understand the scenario before testing
- **Plan Test Cases**: Identify what you want to test
- **Set Expectations**: Know what should happen
- **Prepare Questions**: Have realistic user questions ready

### During Testing
- **Be Consistent**: Use consistent testing approaches
- **Document Issues**: Note any problems or unexpected behavior
- **Test Thoroughly**: Cover all relevant scenarios
- **Monitor State**: Watch the coach state visualizer

### After Testing
- **Reset Scenarios**: Clean up after testing
- **Document Results**: Record findings and issues
- **Update Scenarios**: Modify scenarios based on findings
- **Share Insights**: Communicate results with team

## Troubleshooting Common Issues

### Scenario Won't Start
- **Check Permissions**: Ensure admin access
- **Verify Template**: Check scenario template validity
- **Clear Cache**: Refresh browser or clear cache
- **Check Logs**: Review system logs for errors

### Chat Interface Issues
- **Refresh Page**: Reload the test interface
- **Check Network**: Ensure stable internet connection
- **Clear Browser Data**: Clear cookies and cache
- **Try Different Browser**: Test in alternative browser

### State Inconsistencies
- **Reset Scenario**: Use fresh start to reset state
- **Check Template**: Verify template data is correct
- **Review Actions**: Check for conflicting actions
- **Contact Support**: Report persistent issues

## Related Documentation

- [Scenario Management](./scenario-management) - Creating and editing scenarios
- [Freeze Session](./freeze-session) - Capturing live sessions as scenarios
- [Coach State Visualization](./coach-state-visualization) - Understanding the visualizer
- [Test Scenario API Reference](../api/endpoints/test-scenarios) - Backend API details
