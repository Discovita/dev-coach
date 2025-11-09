/**
 * Represents the current state of an identity within the coaching process.
 * This enum is used to track the lifecycle of an identity, for example,
 * in the `Identity` interface in `client/src/types/identity.ts`.
 */
export enum IdentityState {
  PROPOSED = "proposed",
  ACCEPTED = "accepted",
  REFINEMENT_COMPLETE = "refinement_complete",
  COMMITMENT_COMPLETE = "commitment_complete",
  I_AM_COMPLETE = "i_am_complete",
  VISUALIZATION_COMPLETE = "visualization_complete",
}
