import React from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

/**
 * Modal player for a single Coaching Phase Video (PR 16 shell).
 *
 * Renders a `<video>` element with controls + the video name as the
 * dialog title. Closes on Escape, backdrop click, or the close (X) button
 * provided by `DialogContent`. NONE of those close paths fire any backend
 * action — PR 16 is the visual shell only.
 *
 * PR 17 will add the threshold-gated Continue button + action dispatch
 * (ACK for intros, ACK + START_BREAK for outros).
 */
export interface SessionVideoModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  videoName: string;
  videoUrl: string;
}

export const SessionVideoModal: React.FC<SessionVideoModalProps> = ({
  open,
  onOpenChange,
  videoName,
  videoUrl,
}) => {
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
          data-testid="session-video-element"
          src={videoUrl}
          controls
          preload="metadata"
          className="w-full max-h-[70vh] bg-black"
        >
          <track kind="captions" />
        </video>
      </DialogContent>
    </Dialog>
  );
};
