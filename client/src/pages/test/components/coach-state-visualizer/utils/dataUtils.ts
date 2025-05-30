import { CoachState } from "@/types/coachState";

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
export const getCurrentStateInfo = (
  coachState: CoachState
): Record<string, unknown> => {
  return {
    id: coachState.id,
    user: coachState.user,
    current_phase: coachState.current_phase,
    current_identity: coachState.current_identity,
    proposed_identity: coachState.proposed_identity,
    updated_at: coachState.updated_at,
  };
};
