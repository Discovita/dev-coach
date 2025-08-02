/**
 * Type of action to perform
 */
export enum ActionType {
  CREATE_IDENTITY = "create_identity",
  UPDATE_IDENTITY = "update_identity",
  ACCEPT_IDENTITY = "accept_identity",
  ACCEPT_IDENTITY_REFINEMENT = "accept_identity_refinement",
  ADD_IDENTITY_NOTE = "add_identity_note",
  TRANSITION_PHASE = "transition_phase",
  SELECT_IDENTITY_FOCUS = "select_identity_focus",
  SET_CURRENT_IDENTITY = "set_current_identity",
  UPDATE_WHO_YOU_ARE = "update_who_you_are",
  UPDATE_WHO_YOU_WANT_TO_BE = "update_who_you_want_to_be",
  SKIP_IDENTITY_CATEGORY = "skip_identity_category",
  UNSKIP_IDENTITY_CATEGORY = "unskip_identity_category",
}
