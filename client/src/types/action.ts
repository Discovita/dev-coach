import { Message } from "./message";

/**
 * Represents a single action performed by the coach.
 * This interface matches the database Action model structure.
 * Used in: CoachResponse.actions, UI renderers (renderActionsSection), etc.
 */
export interface Action {
  /** Unique identifier for the action. */
  id: string;
  /** The type of action performed. */
  action_type: string;
  /** Human-readable action type name. */
  action_type_display: string;
  /** Parameters passed to the action (stored as JSON). */
  parameters: Record<string, unknown>;
  /** Natural language description of what the action accomplished. */
  result_summary: string | null;
  /** When the action was performed. */
  timestamp: string;
  /** Formatted timestamp for display. */
  timestamp_formatted: string;
  /** The coach message that triggered this action. */
  coach_message: Message;
  /** Test scenario this action is associated with (for test data isolation). */
  test_scenario: string | null;
}
