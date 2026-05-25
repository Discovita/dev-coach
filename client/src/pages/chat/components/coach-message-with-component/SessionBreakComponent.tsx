import React from "react";
import type { ComponentConfig } from "@/types/componentConfig";
import type { CoachRequest } from "@/types/coachRequest";
import MarkdownRenderer from "@/utils/MarkdownRenderer";

/**
 * Coaching Phase Videos — `SessionBreakComponent` (PR 18).
 *
 * Renders the between-session break card with a single "I'm Ready" button
 * (label + actions come from `config.buttons[0]`, server-baked in
 * `start_break.py`). Click dispatches `{message: button.label, actions:
 * button.actions}` — the canned-response pattern (mirrors
 * `IntroCannedResponseComponent`). The button label becomes a real user
 * `ChatMessage` in chat history; the action chain (`[END_BREAK()]`)
 * closes the break and may emit the next session's intro video.
 *
 * Composer disabling while the break is open is handled separately by
 * `useComposerDisabled` (reads `coachState.on_break`).
 */
export const SessionBreakComponent: React.FC<{
  coachMessage: React.ReactNode;
  config: ComponentConfig;
  onSendUserMessageToCoach: (request: CoachRequest) => void;
  disabled: boolean;
}> = ({ coachMessage, config, onSendUserMessageToCoach, disabled }) => {
  const hasButtons = config.buttons && config.buttons.length > 0;

  return (
    <div
      data-testid="session-break-card"
      className={`_SessionBreakComponent mb-4 p-3.5 pr-4 pl-4 rounded-t-[18px] rounded-br-[18px] rounded-bl-[6px] ${
        hasButtons ? "w-fit max-w-[100%]" : "w-fit max-w-[75%]"
      } shadow-sm animate-fadeIn break-words mr-auto text-[18px] font-medium leading-[1.5] text-black`}
      style={{
        fontFamily: "'Montserrat', sans-serif",
        backgroundColor: "var(--nv-pale-lavender, #eae6fb)",
      }}
    >
      <div className="max-w-[75%]">
        {React.isValidElement(coachMessage) ? (
          coachMessage
        ) : (
          <MarkdownRenderer content={String(coachMessage)} />
        )}
      </div>

      {config.buttons && config.buttons.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2 justify-end">
          {config.buttons.map((button, index) => (
            <button
              key={index}
              onClick={() =>
                onSendUserMessageToCoach({
                  message: button.label,
                  actions: button.actions,
                })
              }
              disabled={disabled}
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
              {button.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
