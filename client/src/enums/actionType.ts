/**
 * Type of action to perform
 */
export enum ActionType {
  CREATE_IDENTITY = "create_identity",
  UPDATE_IDENTITY = "update_identity",
  ACCEPT_IDENTITY = "accept_identity",
  ACCEPT_IDENTITY_REFINEMENT = "accept_identity_refinement",
  ADD_IDENTITY_NOTE = "add_identity_note",
  TRANSITION_STATE = "transition_state",
  SELECT_IDENTITY_FOCUS = "select_identity_focus",
}
