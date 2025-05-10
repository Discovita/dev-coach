/**
 * Type of action to perform
 */
export type ActionType =
  | "create_identity"
  | "update_identity"
  | "accept_identity"
  | "accept_identity_refinement"
  | "add_identity_note"
  | "transition_state"
  | "select_identity_focus";
