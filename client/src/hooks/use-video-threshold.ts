import { useCallback, useState } from "react";

/**
 * Coaching Phase Videos (PR 17) — threshold gate for the video modal's
 * Continue button.
 *
 * Per spec Decision 8: the Continue button stays disabled until the video
 * reaches a threshold, then becomes clickable and remains clickable (sticky).
 *
 *   - Videos LONGER  than `SHORT_VIDEO_CUTOFF_SECONDS` (30s default):
 *     threshold is `END_THRESHOLD_SECONDS` (20s) before the end.
 *   - Videos SHORTER or equal to the cutoff: threshold is the 50% mark.
 *
 * The hook is dumb on purpose — it just consumes `currentTime` and
 * `duration` from the `<video>` element's `timeupdate` event. The caller
 * (`SessionVideoModal`) wires `onTimeUpdate` to the `<video onTimeUpdate>`
 * handler and reads `thresholdReached` to set the Continue button's
 * `disabled` prop.
 *
 * Why a hook and not just a useEffect on currentTime:
 *   - `currentTime` updates ~4 times/sec — a hook keeps the threshold
 *     check local and re-renders only on transitions, not every tick.
 *   - Sticky once-reached behavior is encapsulated here.
 *
 * Reset: passing `key` to the hook in React (`<SessionVideoModal key={...}>`
 * remounts) is the simplest way to reset state when the modal is closed
 * and re-opened.
 */
export const SHORT_VIDEO_CUTOFF_SECONDS = 30;
export const END_THRESHOLD_SECONDS = 20;
export const SHORT_VIDEO_THRESHOLD_FRACTION = 0.5;

export interface UseVideoThresholdResult {
  thresholdReached: boolean;
  onTimeUpdate: (currentTime: number, duration: number) => void;
}

export function useVideoThreshold(): UseVideoThresholdResult {
  const [thresholdReached, setThresholdReached] = useState(false);

  const onTimeUpdate = useCallback(
    (currentTime: number, duration: number) => {
      if (thresholdReached) return;
      if (!Number.isFinite(duration) || duration <= 0) return;

      const thresholdSeconds =
        duration > SHORT_VIDEO_CUTOFF_SECONDS
          ? duration - END_THRESHOLD_SECONDS
          : duration * SHORT_VIDEO_THRESHOLD_FRACTION;

      if (currentTime >= thresholdSeconds) {
        setThresholdReached(true);
      }
    },
    [thresholdReached]
  );

  return { thresholdReached, onTimeUpdate };
}
