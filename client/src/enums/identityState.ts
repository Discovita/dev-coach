/**
 * Represents the current state of an identity within the coaching process.
 * This enum is used to track the lifecycle of an identity, for example,
 * in the `Identity` interface in `client/src/types/identity.ts`.
 */
export enum IdentityState {
  PROPOSED = "proposed",
  ACCEPTED = "accepted",
  REFINEMENT_COMPLETE = "refinement_complete",
  AFFIRMATION_COMPLETE = "affirmation_complete",
  VISUALIZATION_COMPLETE = "visualization_complete",
}
