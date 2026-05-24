/**
 * Frontend component type selector used to render coach components.
 * Must mirror server/enums/component_type.py values.
 */
export enum ComponentType {
  INTRO_CANNED_RESPONSE = "intro_canned_response",
  WARMUP_IDENTITIES = "warmup_identities",
  BRAINSTORMING_IDENTITIES = "brainstorming_identities",
  COMBINE_IDENTITIES = "combine_identities",
  ACCEPT_I_AM = "accept_i_am",
  NEST_IDENTITIES = "nest_identities",
  ARCHIVE_IDENTITY = "archive_identity",
  SUGGEST_I_AM_STATEMENT = "suggest_i_am_statement",
  I_AM_STATEMENTS_SUMMARY = "i_am_statements_summary",
  // Coaching Phase Videos
  SESSION_VIDEO = "session_video",
  SESSION_BREAK = "session_break",
}
