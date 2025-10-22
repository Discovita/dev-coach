/**
 * Type of action to perform
 */
export enum ActionType {
  CREATE_IDENTITY = "create_identity",
  CREATE_MULTIPLE_IDENTITIES = "create_multiple_identities",
  UPDATE_IDENTITY = "update_identity",
  UPDATE_IDENTITY_NAME = "update_identity_name",
  UPDATE_I_AM_STATEMENT = "update_i_am_statement",
  UPDATE_IDENTITY_VISUALIZATION = "update_identity_visualization",
  ACCEPT_IDENTITY = "accept_identity",
  ACCEPT_IDENTITY_REFINEMENT = "accept_identity_refinement",
  ACCEPT_I_AM_STATEMENT = "accept_i_am_statement",
  ACCEPT_IDENTITY_VISUALIZATION = "accept_identity_visualization",
  ADD_IDENTITY_NOTE = "add_identity_note",
  TRANSITION_PHASE = "transition_phase",
  SELECT_IDENTITY_FOCUS = "select_identity_focus",
  SET_CURRENT_IDENTITY = "set_current_identity",
  UPDATE_WHO_YOU_ARE = "update_who_you_are",
  UPDATE_WHO_YOU_WANT_TO_BE = "update_who_you_want_to_be",
  SKIP_IDENTITY_CATEGORY = "skip_identity_category",
  UNSKIP_IDENTITY_CATEGORY = "unskip_identity_category",
  UPDATE_ASKED_QUESTIONS = "update_asked_questions",
  SHOW_ACCEPT_I_AM_COMPONENT = "show_accept_i_am_component",
  SHOW_BRAINSTORMING_IDENTITIES = "show_brainstorming_identities",
  SHOW_COMBINE_IDENTITIES = "show_combine_identities",
  COMBINE_IDENTITIES = "combine_identities",
}
