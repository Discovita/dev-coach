/**
 * Represents a single action performed by the coach.
 * - type: The action name (string).
 * - params: Arbitrary key-value pairs for action parameters, or null if not present.
 * Used in: CoachResponse.actions, UI renderers (renderActionsSection), etc.
 */
export interface Action {
  /** Unique identifier for the action. */
  type: string;
  params: Record<string, unknown> | null;
}
