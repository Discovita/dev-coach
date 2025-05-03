# Coach State Visualizer

## Overview

The Coach State Visualizer is a React component that provides a detailed view into the internal state and operation of the coaching system during test mode. It allows developers and testers to inspect the coach's internal state, actions, and prompts in real-time.

## Key Features

- **Tabbed Interface**: Organizes different aspects of the coach state into separate tabs
- **Collapsible Sections**: Each data section can be expanded/collapsed for easier navigation
- **JSON Content Display**: Shows formatted JSON data with proper indentation
- **Markdown Rendering**: Renders prompts using Markdown for better readability
- **Copy to Clipboard**: Allows copying data to clipboard with a single click
- **Change Detection**: Visual indicators show when content in other tabs has changed
- **Responsive Layout**: Adapts to different screen sizes and orientations

## Component Structure

The component follows a modular architecture:

```
coach-state-visualizer/
├── CoachStateVisualizer.tsx     # Main component
├── types.ts                     # Type definitions
├── index.ts                     # Public exports
├── README.md                    # This documentation
└── utils/
    ├── changeDetection.ts       # Change detection utilities
    ├── dataUtils.ts             # Data manipulation utilities
    ├── index.ts                 # Utility exports
    ├── renderUtils.tsx          # UI rendering functions
    └── tabConfiguration.ts      # Tab settings and configuration
    └── tabContentFactory.tsx    # Factory for tab content
```

## How It Works

### State Tracking

The component maintains several pieces of state:
- **activeTab**: The currently selected tab
- **expandedSections**: Which data sections are expanded/collapsed
- **tabUpdates**: Which tabs have updated content
- **Reference data**: Previous state values for detecting changes

### Tab System

Content is organized into tabs:
- **State & Metadata**: Basic coach state and metadata
- **Prompt Info**: The final prompt sent to the AI
- **Actions**: Available actions and actions taken
- **Identities**: Confirmed and proposed identities
- **Conversation**: The conversation history

### Change Detection

The component shows visual indicators when content in a non-active tab changes:
1. Current state is compared with previous state using deep comparison
2. Changes are detected for relevant sections of each tab
3. A pulsing red dot appears on tabs with updated content
4. The indicator is cleared when you switch to that tab

### Content Rendering

Content rendering is handled by dedicated utility functions:
- **renderJsonSection**: Renders collapsible JSON data sections
- **renderFinalPrompt**: Renders the final prompt with Markdown
- **renderEmptyState**: Shows placeholders when data is empty
- **renderTabContent**: Factory that renders the appropriate content for each tab

## How to Make Changes

### Adding a New Tab

1. Add a new tab name to the `TabName` enum in `types.ts`:
   ```typescript
   export enum TabName {
     STATE = 'state',
     // ... existing tabs
     NEW_TAB = 'new_tab',
   }
   ```

2. Add the tab to the tabs configuration in `tabConfiguration.ts`:
   ```typescript
   export const getTabsConfig = (): TabConfig[] => [
     // ... existing tabs
     { name: TabName.NEW_TAB, label: 'New Tab Label' },
   ];
   ```

3. Add a change detection function in `changeDetection.ts`:
   ```typescript
   export const detectNewTabChanges = (
     prevState: CoachState | null,
     currentState: CoachState
   ): boolean => {
     if (!prevState) return false;
     return hasChanged(prevState.someProperty, currentState.someProperty);
   };
   ```

4. Update the `detectAllTabChanges` function to include your new tab

5. Add a case for your tab in the `renderTabContent` function in `tabContentFactory.tsx`:
   ```typescript
   case TabName.NEW_TAB:
     return (
       <>
         {renderJsonSection(
           'Section Title', 
           data, 
           'sectionKey',
           expandedSections['sectionKey'],
           toggleSection
         )}
       </>
     );
   ```

### Modifying Change Detection

To change how the component detects changes for a specific tab:

1. Locate the relevant detection function in `changeDetection.ts` (e.g., `detectStateTabChanges`)
2. Modify the comparison logic to include or exclude specific properties
3. For complex data, consider updating the `hasChanged` function to handle your specific case

### Styling Changes

Styles are defined in `frontend/apps/coach/src/styles/coach-state-visualizer.css`. The main style sections are:

- `.coach-state-visualizer`: The main container
- `.coach-state-visualizer .tabs`: Tab navigation
- `.coach-state-visualizer .tab`: Individual tabs
- `.coach-state-visualizer .tab-content`: Content area
- `.coach-state-visualizer .state-section`: Collapsible sections
- `.coach-state-visualizer .has-updates`: Update indicator
- `.coach-state-visualizer .json-content`: JSON display
- `.coach-state-visualizer .markdown-prompt-content`: Markdown content

## API Reference

### Props

```typescript
interface CoachStateVisualizerProps {
  coachState: CoachState;          // Current coach state
  lastResponse?: CoachResponse;    // Last API response with prompt
}
```

### Types

| Type | Description |
|------|-------------|
| `TabName` | Enum of available tab names |
| `ExpandedSectionsConfig` | Record of which sections are expanded |
| `TabUpdateStatus` | Record of which tabs have updates |
| `ExtractedActions` | Actions extracted from metadata |

### Utility Functions

| Function | Description |
|----------|-------------|
| `extractActions` | Extracts actions from coach state metadata |
| `renderJsonSection` | Renders a collapsible JSON section |
| `renderFinalPrompt` | Renders the final prompt with Markdown |
| `renderEmptyState` | Renders a placeholder for empty data |
| `detectAllTabChanges` | Detects changes across all tabs |
| `hasChanged` | Performs deep comparison between values |
| `getTabsConfig` | Gets the configuration for all tabs |
| `getDefaultExpandedSections` | Gets default expanded sections config |

## Usage Example

```tsx
import { CoachStateVisualizer } from './components/coach-state-visualizer';

// Inside your component
const [coachState, setCoachState] = useState<CoachState>(initialState);
const [lastResponse, setLastResponse] = useState<CoachResponse | null>(null);

// Update state when API responds
const handleApiResponse = (response: CoachResponse) => {
  setCoachState(response.coach_state);
  setLastResponse(response);
};

// Render the visualizer
return (
  <div className="test-mode-visualizer">
    <CoachStateVisualizer 
      coachState={coachState}
      lastResponse={lastResponse || undefined}
    />
  </div>
);
```

## Performance Considerations

The visualizer is designed to be efficient even with large data:

- Only performs change detection when necessary
- Uses optimized deep comparison for arrays and objects
- Special handling for conversation history (only checks last message)
- Only updates state when actual changes are detected
- Uses refs to avoid unnecessary re-renders