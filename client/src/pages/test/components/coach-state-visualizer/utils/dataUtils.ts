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
    identity_focus: coachState.identity_focus,
    skipped_identity_categories: coachState.skipped_identity_categories,
    who_you_are: coachState.who_you_are,
    who_you_want_to_be: coachState.who_you_want_to_be,
    updated_at: coachState.updated_at,
  };
};
