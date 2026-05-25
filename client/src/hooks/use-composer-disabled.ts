import { useCoachState } from "@/hooks/use-coach-state";
import { useChatMessages } from "@/hooks/use-chat-messages";
import { ComponentType } from "@/enums/componentType";

/**
 * Coaching Phase Videos — composer-disable rule (PR 15 + PR 18).
 *
 * The chat composer disables when any of these are true:
 *   1. A message round-trip is in flight (`isProcessingMessage`).
 *   2. The user is on a between-session break (`coachState.on_break`).
 *   3. The latest coach message carries an unacknowledged `SESSION_VIDEO`
 *      component — i.e., `component_config.component_type === SESSION_VIDEO`
 *      and `component_config.video_key` is NOT in `coachState.shown_videos`.
 *
 * The user must click "I'm Ready" on the break card (which fires
 * END_BREAK) or click Continue on the video modal (which fires
 * ACKNOWLEDGE_SESSION_VIDEO at threshold) before they can type again. This
 * prevents the gate from being bypassed by typing past a video that the
 * coach intentionally injected.
 */
export function useComposerDisabled(isProcessingMessage: boolean): boolean {
  const { coachState } = useCoachState();
  const { chatMessages } = useChatMessages();

  if (isProcessingMessage) return true;
  if (coachState?.on_break === true) return true;

  // Find the most recent coach message — the only one whose component
  // can gate the composer. Historical SESSION_VIDEO cards further up in
  // history don't block input; only the latest one does.
  const messages = chatMessages ?? [];
  let latestCoach = null;
  for (let i = messages.length - 1; i >= 0; i--) {
    if (messages[i].role === "coach") {
      latestCoach = messages[i];
      break;
    }
  }
  if (!latestCoach) return false;

  const cfg = latestCoach.component_config;
  if (cfg?.component_type !== ComponentType.SESSION_VIDEO) return false;

  const videoKey = cfg.video_key;
  if (videoKey === undefined) return false;

  const shownVideos = coachState?.shown_videos ?? [];
  return !shownVideos.includes(videoKey);
}
