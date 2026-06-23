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

/**
 * Session-video key for the identity visualization intro. Acknowledging this
 * video is the true "coaching is finished" moment.
 */
export const VISUALIZATION_INTRO_VIDEO_KEY = "visualization_session_intro";

/**
 * True once the user has actually finished the coaching flow: they are in the
 * identity visualization phase AND have acknowledged the visualization intro
 * video.
 *
 * Why not just the phase? The coach flips `current_phase` to visualization
 * early — during the I-Am transition turn, before the I-Am outro video, the
 * between-session break, and the visualization intro video. Keying off the
 * phase alone fires too soon. Gating on the intro-video acknowledgement
 * sequences correctly: outro → break → intro video → done.
 *
 * This is the shared trigger for both the unlock animation and the
 * "Go to the Studio" chat gate.
 */
export function isCoachingComplete(
  coachState: CoachState | undefined,
): boolean {
  if (coachState?.current_phase !== CoachingPhase.IDENTITY_VISUALIZATION) {
    return false;
  }
  return (coachState.shown_videos ?? []).includes(
    VISUALIZATION_INTRO_VIDEO_KEY,
  );
}
