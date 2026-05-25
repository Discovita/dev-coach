import type { ComponentConfig } from "./componentConfig";

export interface CoachResponse {
  message: string;
  final_prompt?: string;
  component?: ComponentConfig;
  /**
   * Coaching Phase Videos (PR 9): true while the user has an open `Break`
   * row. Mirrored onto the coach response so the composer flips instantly
   * after a turn that opens or closes a break (e.g. `START_BREAK` →
   * `on_break: true`, `END_BREAK` → `on_break: false`) without waiting
   * for the `coachState` query to refetch.
   */
  on_break?: boolean;
}
