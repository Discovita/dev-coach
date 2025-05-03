import { CoachState, CoachResponse, Action } from '@/types/apiTypes';
import { ExtractedActions } from '../types';

// Map to track actions by user session
// Key is user name + first message timestamp (as a unique session identifier)
const actionsBySession: Record<string, Action[]> = {};

/**
 * Gets a unique identifier for the current user session
 *
 * @param state - The coach state containing user information
 * @returns A string identifier unique to this session
 */
const getSessionKey = (state: CoachState): string => {
  const userName = state.user_profile?.name || 'unknown';
  const firstMsgTime =
    state.conversation_history && state.conversation_history.length > 0
      ? JSON.stringify(state.conversation_history[0])
      : Date.now().toString();

  return `${userName}-${firstMsgTime}`;
};

/**
 * Extracts available actions and actions taken from the coach state metadata
 * and direct actions from the response, maintaining a history of all actions seen
 *
 * @param coachState - The current state of the coach
 * @param lastResponse - The last API response which may contain actions
 * @returns Object containing available actions and actions taken
 */
export const extractActions = (
  coachState: CoachState,
  lastResponse?: CoachResponse
): ExtractedActions => {
  const metadata = coachState.metadata || {};
  const sessionKey = getSessionKey(coachState);

  // Initialize session entry if needed
  if (!actionsBySession[sessionKey]) {
    actionsBySession[sessionKey] = [];
  }

  // Get new explicit actions from response
  const responseActions = lastResponse?.actions || [];

  // Add response actions to our session history if they're new
  if (responseActions.length > 0) {
    responseActions.forEach(responseAction => {
      const actionAsString = JSON.stringify(responseAction);
      const isDuplicate = actionsBySession[sessionKey].some(
        existingAction => JSON.stringify(existingAction) === actionAsString
      );

      if (!isDuplicate) {
        actionsBySession[sessionKey].push(responseAction);
      }
    });
  }

  // Return both metadata actions and our accumulated history for this session
  return {
    availableActions: (metadata.available_actions as string[]) || [],
    actionsTaken: actionsBySession[sessionKey],
  };
};

/**
 * Copies JSON data to clipboard with proper formatting
 *
 * @param data - Data to copy to clipboard
 */
export const copyToClipboard = (data: any): void => {
  navigator.clipboard.writeText(JSON.stringify(data, null, 2));
};

/**
 * Extracts current state information from coach state
 *
 * @param coachState - The current state of the coach
 * @returns Object containing essential state information
 */
export const getCurrentStateInfo = (coachState: CoachState): object => {
  return {
    current_state: coachState.current_state,
    current_identity_id: coachState.current_identity_id,
  };
};
