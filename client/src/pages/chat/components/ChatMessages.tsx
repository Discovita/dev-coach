import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CoachMessage } from "@/pages/chat/components/CoachMessage";
import { CoachMessageWithComponent } from "@/pages/chat/components/coach-message-with-component/CoachMessageWithComponent.tsx";
import { UserMessage } from "@/pages/chat/components/UserMessage";
import MarkdownRenderer from "@/utils/MarkdownRenderer";
import { LoadingBubbles } from "@/pages/chat/components/LoadingBubbles";
import type { Message } from "@/types/message";
import type { CoachRequest } from "@/types/coachRequest";
import type { ComponentConfig } from "@/types/componentConfig";

/**
 * ChatMessages component is used to render the chat messages in both the
 *
 */

/**
 * Props for ChatMessages
 * ---------------------
 * - messages: The full chat message history to render (array of Message objects)
 * - isProcessingMessage: Whether a message is being sent (shows loading bubbles)
 * - coachState: The current coach state (for proposed identity)
 * - handleIdentityChoice: Handler for when a user selects an identity
 * - messagesEndRef: Ref to scroll to the bottom of the messages
 *
 * Used by: ChatInterface.tsx
 */
interface ChatMessagesProps {
  messages: Message[];
  isProcessingMessage: boolean;
  messagesEndRef: React.RefObject<HTMLDivElement | null>;
  /** Latest component config to render for the newest coach message (or null) */
  componentConfig?: ComponentConfig | null;
  /** Handler for component button selection (sends a CoachRequest) */
  onSendUserMessageToCoach: (request: CoachRequest) => void;
}

// Shared motion config for chat rows. `layout` makes height/position changes
// (e.g. the break card collapsing to its "Took a break" pill, or rows
// reflowing when a new card appears) tween smoothly instead of snapping.
// New rows fade + rise in; removed rows (optimistic message, loading bubble)
// fade out.
const ROW_TRANSITION = { duration: 0.25, ease: "easeOut" } as const;
const rowMotion = {
  layout: true,
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0 },
  transition: ROW_TRANSITION,
} as const;

export const ChatMessages: React.FC<ChatMessagesProps> = ({
  messages,
  isProcessingMessage,
  messagesEndRef,
  componentConfig,
  onSendUserMessageToCoach,
}) => {
  return (
    // `layoutScroll` tells framer-motion to account for this element's scroll
    // offset when measuring `layout` animations, so rows animate from the
    // correct on-screen position instead of flying in when the list is
    // scrolled.
    <motion.div
      layoutScroll
      className="_ChatMessages scrollbar not-last:flex-grow overflow-y-auto sm:p-6 bg-gold-50  dark:bg-[#333333]"
    >
      <AnimatePresence initial={false}>
        {messages.map((message: Message, index: number) => (
          <motion.div key={`${message.timestamp}-${message.role}`} {...rowMotion}>
            {message.role === "coach" ? (
              (() => {
                const isLastCoachMessage = index === messages.length - 1;
                let componentToRender = null;

                if (isLastCoachMessage) {
                  // Prefer the in-memory cache when not processing (freshest
                  // server response). Fall through to `message.component_config`
                  // for server-seeded cards (welcome SESSION_VIDEO,
                  // post-END_BREAK intros) — those represent persisted
                  // history and stay visible even during in-flight requests,
                  // so clicking Continue doesn't blink the card out while
                  // we wait for the response.
                  componentToRender =
                    (!isProcessingMessage && componentConfig) ||
                    message.component_config ||
                    null;
                } else {
                  // For all other coach messages, ONLY check message.component_config
                  componentToRender = message.component_config || null;
                }

                return componentToRender ? (
                  <CoachMessageWithComponent
                    componentConfig={componentToRender}
                    onSendUserMessageToCoach={onSendUserMessageToCoach}
                    disabled={isProcessingMessage}
                  >
                    <MarkdownRenderer content={message.content} />
                  </CoachMessageWithComponent>
                ) : (
                  <CoachMessage>
                    <MarkdownRenderer content={message.content} />
                  </CoachMessage>
                );
              })()
            ) : message.role === "user" ? (
              <UserMessage>{message.content}</UserMessage>
            ) : (
              <div className="mb-4 p-3.5 pr-4 pl-4 rounded-[18px] max-w-[85%] leading-[1.5] shadow-sm break-words mx-auto bg-red-500/70 text-center font-medium">
                {message.content}
              </div>
            )}
          </motion.div>
        ))}
        {isProcessingMessage && (
          <motion.div key="loading-bubbles" {...rowMotion}>
            <CoachMessage>
              <LoadingBubbles />
            </CoachMessage>
          </motion.div>
        )}
      </AnimatePresence>
      {/* Dummy div to scroll to bottom */}
      <div ref={messagesEndRef} />
    </motion.div>
  );
};
