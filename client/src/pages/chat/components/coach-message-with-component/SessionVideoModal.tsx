import React, { useRef } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { ComponentAction } from "@/types/componentConfig";
import { useVideoThreshold } from "@/hooks/use-video-threshold";

/**
 * Modal player for a single Coaching Phase Video (PR 16 shell, PR 17
 * threshold gate + dispatch).
 *
 * Renders a `<video>` element with native controls + the video name as
 * the dialog title. Closes on Escape, backdrop click, or the close (X)
 * button provided by `DialogContent`. NONE of those close paths fire any
 * backend action — only the explicit Continue button does.
 *
 * Continue button rules (PR 17):
 *   - Rendered only when the video has NOT yet been acknowledged.
 *     (Acked / "Watch Again" modal stays Continue-less per spec
 *     Decision 8.)
 *   - Disabled until the threshold from `useVideoThreshold` is reached
 *     (20s before end for videos > 30s; 50% mark for ≤ 30s).
 *   - On click, dispatches the bundled actions baked into the
 *     `component_config.buttons[0].actions` by the server (server is the
 *     single source of truth for which actions fire — intro = `[ACK]`;
 *     outro = `[ACK, START_BREAK]`) via `{message: null, ...}`.
 *   - Modal closes after dispatch.
 */
export interface SessionVideoModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  videoName: string;
  videoUrl: string;
  /**
   * Whether this modal is for the "Watch Again" (acked) case. When true,
   * no Continue button renders; closing the modal does nothing.
   */
  acknowledged: boolean;
  /**
   * Actions to dispatch when the Continue button is clicked. Copied
   * verbatim from `component_config.buttons[0].actions`. Ignored when
   * `acknowledged` is true.
   */
  actions: ComponentAction[];
  /**
   * Called with the bundled actions when Continue is clicked. The card
   * wires this to `onSendUserMessageToCoach({message: null, actions})`.
   */
  onContinue: (actions: ComponentAction[]) => void;
}

export const SessionVideoModal: React.FC<SessionVideoModalProps> = ({
  open,
  onOpenChange,
  videoName,
  videoUrl,
  acknowledged,
  actions,
  onContinue,
}) => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const { thresholdReached, onTimeUpdate } = useVideoThreshold();

  const handleContinue = () => {
    onContinue(actions);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        data-testid="session-video-modal"
        className="sm:max-w-3xl p-0 overflow-hidden"
      >
        <DialogHeader className="px-6 pt-6">
          <DialogTitle>{videoName}</DialogTitle>
          <DialogDescription className="sr-only">
            Watch the {videoName} video.
          </DialogDescription>
        </DialogHeader>
        <video
          ref={videoRef}
          data-testid="session-video-element"
          src={videoUrl}
          controls
          preload="metadata"
          className="w-full max-h-[70vh] bg-black"
          onTimeUpdate={(e) => {
            const el = e.currentTarget;
            onTimeUpdate(el.currentTime, el.duration);
          }}
        >
          <track kind="captions" />
        </video>
        {!acknowledged && actions.length > 0 && (
          <div className="px-6 pb-6 flex justify-end">
            <button
              type="button"
              data-testid="session-video-continue"
              onClick={handleContinue}
              disabled={!thresholdReached}
              className="px-4 py-2 text-sm font-medium rounded-md transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              style={{
                backgroundColor: thresholdReached
                  ? "var(--nv-royal-purple, #531e96)"
                  : "var(--nv-pale-lavender, #eae6fb)",
                color: thresholdReached ? "white" : "rgba(0,0,0,0.5)",
              }}
            >
              Continue
            </button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};
