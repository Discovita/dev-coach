import { CoachResponse } from "@/types/coachResponse";
import { CoachState } from "@/types/coachState";
import { ExtractedActions } from "../types";

/**
 * Extracts available actions and actions taken from the coach state metadata
 * and direct actions from the response, maintaining a history of all actions seen.
 *
 * With the new model, there is only a single session per user, so we do not track by session.
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

  // Available actions from metadata (if present)
  const availableActions = (metadata.available_actions as string[]) || [];

  // Actions taken: if the last response has actions, use those; otherwise, empty array
  const actionsTaken = lastResponse?.actions || [];

  return {
    availableActions,
    actionsTaken,
  };
};

/**
 * Copies JSON data to clipboard with proper formatting
 *
 * @param data - Data to copy to clipboard
 */
export const copyToClipboard = (data: unknown): void => {
  navigator.clipboard.writeText(JSON.stringify(data, null, 2));
};

/**
 * Extracts current state information from coach state
 *
 * @param coachState - The current state of the coach
 * @returns Object containing essential state information
 */
export const getCurrentStateInfo = (coachState: CoachState): Record<string, unknown> => {
  return {
    id: coachState.id,
    user: coachState.user,
    current_state: coachState.current_state,
    current_identity: coachState.current_identity,
    proposed_identity: coachState.proposed_identity,
    goals: coachState.goals,
    updated_at: coachState.updated_at,
  };
};
