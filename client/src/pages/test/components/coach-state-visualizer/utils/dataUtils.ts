import type { CoachState } from "@/types/coachState";

export const copyToClipboard = (data: unknown): void => {
  navigator.clipboard.writeText(JSON.stringify(data, null, 2));
};

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
