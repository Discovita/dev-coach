---
sidebar_position: 3
---

# Coach State Visualization

The Coach State Visualizer is a powerful debugging and monitoring tool that provides real-time insight into the internal state and operation of the coaching system. It displays comprehensive information about the coach's state, actions, prompts, identities, and conversation history in an organized, tabbed interface. The visualizer is present anytime you access a coach session from within the Test tab available to Admins.

---

## Overview

The visualizer consists of two main components:

- **CoachStateVisualizer**: For monitoring regular user sessions
- **TestScenarioCoachStateVisualizer**: For monitoring test scenario sessions

Both components provide identical functionality but fetch data from different sources using specialized hooks.

> **📋 For detailed information about session types and system architecture, see [Session Types and Architecture](./overview#session-types-and-architecture) in the overview.**

## Key Features

### Tabbed Interface

The visualizer organizes data into five main tabs:

- **State & Metadata**: Current coaching phase, identity focus, and progress data
- **Prompt Info**: The final prompt sent to the AI for the last response
- **Actions**: History of actions taken by the system and available actions
- **Identities**: Confirmed identities and any proposed identity
- **Conversation**: Complete chat message history

### Real-Time Updates

- **Change Detection**: Visual indicators show when content in other tabs has changed
- **Pulsing Indicators**: Red dots appear on tabs with updated content
- **Automatic Refresh**: Data updates automatically as the coaching session progresses

### Interactive Elements

- **Collapsible Sections**: Each data section can be expanded/collapsed
- **Copy to Clipboard**: One-click copying of data for debugging
- **JSON Formatting**: Properly formatted JSON display with syntax highlighting
- **Markdown Rendering**: Prompts are rendered using Markdown for readability

## Data Sources

### Regular User Sessions

The `CoachStateVisualizer` fetches data using these hooks:

- **useCoachState()**: Fetches coach state from `/user/me/coach-state/`
- **useChatMessages()**: Fetches chat history from `/user/me/chat-messages/`
- **useIdentities()**: Fetches identities from `/user/me/identities/`
- **useActions()**: Fetches actions from `/user/me/actions/`
- **useFinalPrompt()**: Retrieves the latest final prompt from cache

### Test Scenario Sessions

The `TestScenarioCoachStateVisualizer` uses specialized test scenario hooks:

- **useTestScenarioUserCoachState(testUserId)**: Fetches coach state from `/test-user/{userId}/coach-state/`
- **useTestScenarioChatMessages(testUserId)**: Fetches chat history from `/test-user/{userId}/chat-messages/`
- **useTestScenarioUserIdentities(testUserId)**: Fetches identities from `/test-user/{userId}/identities/`
- **useTestScenarioUserActions(testUserId)**: Fetches actions from `/test-user/{userId}/actions/`
- **useTestScenarioUserFinalPrompt(testUserId)**: Retrieves the latest final prompt from cache

## API Endpoints Used

### Regular User Endpoints

| Endpoint                  | Method | Description            | Used By         |
| ------------------------- | ------ | ---------------------- | --------------- |
| `/user/me/coach-state/`   | GET    | Current coaching state | useCoachState   |
| `/user/me/chat-messages/` | GET    | Chat message history   | useChatMessages |
| `/user/me/identities/`    | GET    | User identities        | useIdentities   |
| `/user/me/actions/`       | GET    | Action history         | useActions      |

### Test Scenario Endpoints

| Endpoint                             | Method | Description              | Used By                         |
| ------------------------------------ | ------ | ------------------------ | ------------------------------- |
| `/test-user/{userId}/coach-state/`   | GET    | Test user coaching state | useTestScenarioUserCoachState   |
| `/test-user/{userId}/chat-messages/` | GET    | Test user chat history   | useTestScenarioChatMessages |
| `/test-user/{userId}/identities/`    | GET    | Test user identities     | useTestScenarioUserIdentities   |
| `/test-user/{userId}/actions/`       | GET    | Test user actions        | useTestScenarioUserActions      |

## Tab Content Details

### State & Metadata Tab

Displays the current coaching state including:

- **Current Phase**: Active coaching phase (INTRODUCTION, GET_TO_KNOW_YOU, etc.)
- **Identity Focus**: Current focus identity category
- **Skipped Categories**: Identity categories the user has chosen to skip
- **Who You Are**: Current self-perception statements
- **Who You Want to Be**: Aspirational identity statements
- **Asked Questions**: Questions already asked during the session
- **Current Identity**: Currently selected identity (if any)
- **Proposed Identity**: Identity being proposed (if any)

![Coach State Viewer - State & Metadata Tab](/img/coach-state-viewer-coach-state.png)

_Figure 1: The State & Metadata tab showing current coaching phase, identity focus, and other state information_

### Prompt Info Tab

Shows the final prompt that was sent to the AI for the last response:

- **Formatted Display**: Rendered using Markdown for readability
- **Collapsible View**: Can be expanded/collapsed for space management
- **Copy Functionality**: Easy copying for debugging purposes

![Coach State Viewer - Final Prompt Tab](/img/coach-state-viewer-final-prompt.png)

_Figure 2: The Prompt Info tab showing the final prompt sent to the AI with Markdown formatting_

### Actions Tab

Displays two main sections:

#### Actions History

- **Chronological List**: All actions taken by the system, ordered by timestamp
- **Action Details**: Type, parameters, result summary, and timestamp
- **Coach Message Link**: Links to the message that triggered each action

![Coach State Viewer - Actions History Tab](/img/coach-state-viewer-actions-history.png)

_Figure 3: The Actions tab showing action history with details and timestamps_

#### Available Actions

- **Current Actions**: Actions currently available to the coach
- **JSON Format**: Raw data display for debugging

### Identities Tab

Shows identity information in two sections:

#### Confirmed Identities

- **Identity List**: All accepted identities with full details
- **Identity Cards**: Styled display of each identity
- **Details**: Name, category, "I Am" Statement, visualization, and notes

![Coach State Viewer - Identities Tab](/img/coach-state-viewer-identities.png)

_Figure 4: The Identities tab showing confirmed identities with styled identity cards_

#### Proposed Identity

- **Current Proposal**: Any identity currently being proposed
- **Preview**: Shows the identity before acceptance

### Conversation Tab

Displays the complete chat history:

- **Chronological Order**: Messages in timestamp order
- **Role Identification**: Clear distinction between user and coach messages
- **JSON Format**: Raw data for debugging purposes

![Coach State Viewer - Conversation History Tab](/img/coach-state-viewer-conversation-history.png)

_Figure 5: The Conversation tab showing complete chat message history in chronological order_

## Change Detection System

The visualizer implements sophisticated change detection:

### How It Works

1. **Previous State Tracking**: Uses `usePrevious` hook to track previous values
2. **Deep Comparison**: Compares current and previous states using JSON.stringify
3. **Tab-Specific Detection**: Different detection logic for each tab type
4. **Visual Indicators**: Pulsing red dots on tabs with changes

### Detection Logic

- **State Tab**: Compares entire coach state object
- **Prompt Tab**: Compares final prompt string
- **Actions Tab**: Compares actions array
- **Identities Tab**: Compares coach state (for proposed identity changes)
- **Conversation Tab**: Compares chat messages array

### User Experience

- **Visited Tabs**: Only shows indicators for tabs the user has visited
- **Automatic Clearing**: Indicators clear when switching to the updated tab
- **Non-Intrusive**: Doesn't interrupt the user's current workflow

## Technical Implementation

### Component Architecture

```
coach-state-visualizer/
├── CoachStateVisualizer.tsx           # Main component for regular sessions
├── TestScenarioCoachStateVisualizer.tsx # Main component for test scenarios
├── types.ts                           # Type definitions
├── index.ts                           # Public exports
└── utils/
    ├── tabContentFactory.tsx          # Tab content rendering
    ├── renderUtils.tsx                # UI rendering functions
    ├── tabConfiguration.ts            # Tab settings
    ├── dataUtils.ts                   # Data manipulation
    ├── IdentityItem.tsx               # Identity display component
    └── ActionItem.tsx                 # Action display component
```

### Data Flow

1. **Hook Initialization**: Components initialize data fetching hooks
2. **Data Fetching**: Hooks fetch data from respective API endpoints
3. **State Management**: Component manages UI state (active tab, expanded sections)
4. **Change Detection**: Previous values are compared with current values
5. **Rendering**: Tab content is rendered based on current data and UI state

### Performance Considerations

- **Optimized Queries**: Uses TanStack Query for efficient caching and updates
- **Selective Rendering**: Only renders active tab content
- **Change Detection**: Efficient deep comparison using JSON.stringify
- **Memory Management**: Proper cleanup of previous state references

## Related Documentation

- [Test Scenario Overview](./overview) - Understanding test scenarios
- [Scenario Management](./scenario-management) - Managing test scenarios
- [Actions API Reference](../api/endpoints/actions) - Action endpoint documentation
- [Users API Reference](../api/endpoints/users) - User data endpoints
- [Test Users API Reference](../api/endpoints/test-users) - Test user endpoints
