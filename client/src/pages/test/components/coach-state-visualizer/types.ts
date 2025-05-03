import { CoachResponse, CoachState, Action } from '@/types/apiTypes';

/**
 * CoachStateVisualizer Component Props
 *
 * @param coachState - The current state of the coach
 * @param lastResponse - The last API response object containing prompt and other metadata
 */
export interface CoachStateVisualizerProps {
  coachState: CoachState;
  lastResponse?: CoachResponse;
}

/**
 * Actions extracted from the coach state metadata
 */
export interface ExtractedActions {
  availableActions?: string[];
  actionsTaken?: Action[];
}

/**
 * Tab names for the state visualizer
 */
export enum TabName {
  STATE = 'state',
  PROMPT = 'prompt',
  ACTIONS = 'actions',
  IDENTITIES = 'identities',
  CONVERSATION = 'conversation',
}

/**
 * Configuration for expandable sections
 */
export interface ExpandedSectionsConfig {
  [key: string]: boolean;
}

/**
 * Record of tabs with updated content
 */
export type TabUpdateStatus = {
  [key in TabName]?: boolean;
};

/**
 * Tab configuration with labels and update status
 */
export interface TabConfig {
  name: TabName;
  label: string;
}
