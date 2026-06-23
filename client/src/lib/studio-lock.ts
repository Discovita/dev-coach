import { CoachingPhase } from "@/enums/coachingPhase";
import type { CoachState } from "@/types/coachState";

/**
 * User-facing message shown when someone tries to open the Studio before
 * it has been unlocked. Shared by the nav (desktop + mobile) and the
 * /studio route guard so the wording stays consistent.
 */
export const STUDIO_LOCKED_MESSAGE = "This isn't available yet.";

/**
 * The Studio unlocks only once the user reaches the identity visualization
 * phase. Any earlier phase — or an as-yet-unknown coach state (still
 * loading / failed to load) — is treated as locked, so we never flash an
 * unlocked Studio to a user who hasn't earned it.
 */
export function isStudioLocked(coachState: CoachState | undefined): boolean {
  return coachState?.current_phase !== CoachingPhase.IDENTITY_VISUALIZATION;
}
