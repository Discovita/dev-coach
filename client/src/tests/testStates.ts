import { CoachState } from '../types/apiTypes';

// Import test state JSON files
import emptyStateJson from './states/empty_state.json';
import refinementTestCaseJson from './states/refinement_test_case.json';

export interface TestState {
  name: string;
  description: string;
  coach_state: CoachState;
}

// Load test states from JSON files
export const testStates: Record<string, TestState> = {
  emptyState: emptyStateJson as TestState,
  refinementTestCase: refinementTestCaseJson as TestState,
};
