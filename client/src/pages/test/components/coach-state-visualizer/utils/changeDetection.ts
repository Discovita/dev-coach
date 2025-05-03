import { CoachResponse, CoachState } from '@/types/apiTypes';
import { TabName, TabUpdateStatus, ExtractedActions } from '../types';

/**
 * Performs a deep comparison between two objects to detect changes
 *
 * @param prev - Previous value
 * @param current - Current value
 * @returns True if values are different
 */
export const hasChanged = (prev: any, current: any): boolean => {
  try {
    // Handle null/undefined cases
    if (prev === current) return false;
    if (prev === null || prev === undefined || current === null || current === undefined) {
      return prev !== current;
    }

    // Handle arrays
    if (Array.isArray(prev) && Array.isArray(current)) {
      if (prev.length !== current.length) return true;

      // For conversation history, only check last message to avoid
      // excessive re-renders for long conversations
      if (
        prev.length > 0 &&
        typeof prev[0] === 'object' &&
        prev[0] &&
        'role' in prev[0] &&
        'content' in prev[0]
      ) {
        if (prev.length !== current.length) return true;
        return hasChanged(prev[prev.length - 1], current[current.length - 1]);
      }

      // For other arrays, check length first for quick comparison
      if (prev.length !== current.length) return true;

      // Then check key elements to avoid unnecessary JSON stringification
      if (prev.length > 0) {
        // Check first and last elements as a quick test
        if (hasChanged(prev[0], current[0])) return true;
        if (hasChanged(prev[prev.length - 1], current[current.length - 1])) return true;
      }

      // Finally, do a full comparison if needed
      const prevStr = JSON.stringify(prev);
      const currStr = JSON.stringify(current);
      return prevStr !== currStr;
    }

    // Handle primitive values
    if (typeof prev !== 'object' || typeof current !== 'object') {
      return prev !== current;
    }

    // Handle objects - convert to string but catch any circular reference errors
    const prevStr = JSON.stringify(prev);
    const currStr = JSON.stringify(current);
    return prevStr !== currStr;
  } catch (error) {
    // If we encounter errors (like circular references), do simple comparison
    console.warn('Error in change detection, falling back to reference check:', error);
    return prev !== current;
  }
};

/**
 * Detects changes in STATE tab data
 */
export const detectStateTabChanges = (
  prevState: CoachState | null,
  currentState: CoachState
): boolean => {
  if (!prevState) return false;

  return (
    hasChanged(prevState.current_state, currentState.current_state) ||
    hasChanged(prevState.current_identity_id, currentState.current_identity_id) ||
    hasChanged(prevState.user_profile, currentState.user_profile) ||
    hasChanged(prevState.metadata, currentState.metadata)
  );
};

/**
 * Detects changes in PROMPT tab data
 */
export const detectPromptTabChanges = (
  prevResponse: CoachResponse | undefined,
  currentResponse: CoachResponse | undefined
): boolean => {
  if (!prevResponse && !currentResponse) return false;
  if (!prevResponse || !currentResponse) return true;

  if (!prevResponse.final_prompt && currentResponse.final_prompt) return true;
  if (prevResponse.final_prompt && !currentResponse.final_prompt) return true;

  return hasChanged(prevResponse.final_prompt, currentResponse.final_prompt);
};

/**
 * Detects changes in ACTIONS tab data
 */
export const detectActionsTabChanges = (
  prevActions: ExtractedActions | null,
  currentActions: ExtractedActions,
  prevResponse?: CoachResponse,
  currentResponse?: CoachResponse
): boolean => {
  if (!prevActions) return false;

  // Check if response actions have changed
  const prevResponseActions = prevResponse?.actions || [];
  const currentResponseActions = currentResponse?.actions || [];

  if (hasChanged(prevResponseActions, currentResponseActions)) {
    return true;
  }

  return (
    hasChanged(prevActions.actionsTaken, currentActions.actionsTaken) ||
    hasChanged(prevActions.availableActions, currentActions.availableActions)
  );
};

/**
 * Detects changes in IDENTITIES tab data
 */
export const detectIdentitiesTabChanges = (
  prevState: CoachState | null,
  currentState: CoachState
): boolean => {
  if (!prevState) return false;

  // Check for changes in lengths first for quick comparison
  const prevIdentitiesLength = prevState.identities?.length || 0;
  const currentIdentitiesLength = currentState.identities?.length || 0;

  if (prevIdentitiesLength !== currentIdentitiesLength) return true;

  return (
    hasChanged(prevState.identities, currentState.identities) ||
    hasChanged(prevState.proposed_identity, currentState.proposed_identity)
  );
};

/**
 * Detects changes in CONVERSATION tab data
 */
export const detectConversationTabChanges = (
  prevState: CoachState | null,
  currentState: CoachState
): boolean => {
  if (!prevState) return false;

  // Quick check for conversation length change
  const prevLength = prevState.conversation_history?.length || 0;
  const currentLength = currentState.conversation_history?.length || 0;

  if (prevLength !== currentLength) return true;

  // If same length, check if last message changed
  if (prevLength > 0 && currentLength > 0) {
    const prevLast = prevState.conversation_history?.[prevLength - 1];
    const currentLast = currentState.conversation_history?.[currentLength - 1];

    return hasChanged(prevLast, currentLast);
  }

  return false;
};

/**
 * Detects all tab changes and returns a map of tabs with changes
 */
export const detectAllTabChanges = (
  prevState: CoachState | null,
  currentState: CoachState,
  prevResponse: CoachResponse | undefined,
  currentResponse: CoachResponse | undefined,
  prevActions: ExtractedActions | null,
  currentActions: ExtractedActions,
  currentTab: TabName
): TabUpdateStatus => {
  const updates: TabUpdateStatus = {};

  // Only mark tabs as updated if they aren't the current tab
  if (currentTab !== TabName.STATE) {
    updates[TabName.STATE] = detectStateTabChanges(prevState, currentState);
  }

  if (currentTab !== TabName.PROMPT) {
    updates[TabName.PROMPT] = detectPromptTabChanges(prevResponse, currentResponse);
  }

  if (currentTab !== TabName.ACTIONS) {
    updates[TabName.ACTIONS] = detectActionsTabChanges(
      prevActions,
      currentActions,
      prevResponse,
      currentResponse
    );
  }

  if (currentTab !== TabName.IDENTITIES) {
    updates[TabName.IDENTITIES] = detectIdentitiesTabChanges(prevState, currentState);
  }

  if (currentTab !== TabName.CONVERSATION) {
    updates[TabName.CONVERSATION] = detectConversationTabChanges(prevState, currentState);
  }

  return updates;
};
