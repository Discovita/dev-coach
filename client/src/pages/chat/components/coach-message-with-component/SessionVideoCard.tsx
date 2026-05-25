import React, { useState } from "react";
import type { ComponentConfig } from "@/types/componentConfig";
import { useCoachState } from "@/hooks/use-coach-state";
import { CoachMessage } from "@/pages/chat/components/CoachMessage";
import { SessionVideoModal } from "@/pages/chat/components/coach-message-with-component/SessionVideoModal";

/**
 * Coaching Phase Videos — `SessionVideoCard` (PR 16 shell).
 *
 * Renders the thin video card the LLM (or the welcome / break flow)
 * emits inline in chat:
 *
 *   ┌──────────────────────────────────────┐
 *   │  <Video Name>             [ Watch ]  │
 *   └──────────────────────────────────────┘
 *
 * The button label derives from `coachState.shown_videos`:
 *   - "Watch"        when the video_key has NOT been acknowledged
 *   - "Watch Again"  when it HAS been acknowledged
 *
 * Click → opens the modal player (`SessionVideoModal`). The modal in
 * PR 16 is shell-only: Esc / backdrop / X close it with no action
 * dispatch. PR 17 adds the threshold-gated Continue button + actions.
 *
 * If the coach message also carries text (the transition-turn case where
 * the LLM speaks AND a card is attached to the same row), it's rendered
 * above the card via a regular `<CoachMessage>` bubble. For the welcome
 * card + post-break intro card cases (`content === ""`), the text bubble
 * is suppressed and only the thin card renders.
 *
 * Per spec Decision 8 — `Watch Again` keeps its button even on historical
 * cards because it's frontend-only (opens the same modal, no actions
 * fire). This is the intentional deviation from the "strip all buttons
 * from historical components" persistent-component convention.
 */
export interface SessionVideoCardProps {
  coachMessage: React.ReactNode;
  config: ComponentConfig;
}

function extractContentString(node: React.ReactNode): string {
  // ChatMessages passes `<MarkdownRenderer content={message.content} />` as
  // children. Inspect the `content` prop to decide whether to render a
  // text bubble above the card. Defensive: if the shape changes, fall back
  // to showing the bubble (safer than hiding LLM text).
  if (React.isValidElement(node)) {
    const props = (node as React.ReactElement).props as
      | { content?: unknown }
      | undefined;
    if (props && typeof props.content === "string") {
      return props.content;
    }
  }
  return "";
}

export const SessionVideoCard: React.FC<SessionVideoCardProps> = ({
  coachMessage,
  config,
}) => {
  const { coachState } = useCoachState();
  const [open, setOpen] = useState(false);

  const videoName = config.video_name ?? "Session Video";
  const videoUrl = config.video_url ?? "";
  const videoKey = config.video_key;

  const acknowledged =
    videoKey !== undefined &&
    Array.isArray(coachState?.shown_videos) &&
    coachState!.shown_videos!.includes(videoKey);

  const textContent = extractContentString(coachMessage);
  const hasText = textContent.trim().length > 0;

  return (
    <div className="_SessionVideoCard-wrapper">
      {hasText && <CoachMessage>{coachMessage}</CoachMessage>}

      <div
        data-testid="session-video-card"
        className="_SessionVideoCard mb-4 p-3.5 pr-4 pl-4 rounded-t-[18px] rounded-br-[18px] rounded-bl-[6px] w-fit max-w-[100%] shadow-sm animate-fadeIn break-words mr-auto flex items-center gap-4"
        style={{
          fontFamily: "'Montserrat', sans-serif",
          backgroundColor: "var(--nv-pale-lavender, #eae6fb)",
        }}
      >
        <span className="text-[18px] font-medium leading-[1.5] text-black">
          {videoName}
        </span>
        <button
          type="button"
          onClick={() => setOpen(true)}
          className="px-3 py-1.5 text-sm font-medium rounded-md transition-colors cursor-pointer"
          style={{
            backgroundColor: "var(--nv-royal-purple, #531e96)",
            color: "white",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor =
              "var(--nv-violet-blue, #6a5ffb)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor =
              "var(--nv-royal-purple, #531e96)";
          }}
        >
          {acknowledged ? "Watch Again" : "Watch"}
        </button>
      </div>

      <SessionVideoModal
        open={open}
        onOpenChange={setOpen}
        videoName={videoName}
        videoUrl={videoUrl}
      />
    </div>
  );
};
