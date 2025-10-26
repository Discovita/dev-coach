import React from "react";
import { CoachMessage } from "@/pages/chat/components/CoachMessage";
import { CoachMessageWithComponent } from "@/pages/chat/components/coach-message-with-component.tsx/CoachMessageWithComponent";
import { UserMessage } from "@/pages/chat/components/UserMessage";
import MarkdownRenderer from "@/utils/MarkdownRenderer";
import { LoadingBubbles } from "@/pages/chat/components/LoadingBubbles";
import { Message } from "@/types/message";
import { CoachRequest } from "@/types/coachRequest";
import { ComponentConfig } from "@/types/componentConfig";

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

export const ChatMessages: React.FC<ChatMessagesProps> = ({
  messages,
  isProcessingMessage,
  messagesEndRef,
  componentConfig,
  onSendUserMessageToCoach,
}) => {
  return (
    <div className="_ChatMessages scrollbar not-last:flex-grow overflow-y-auto p-6 bg-gold-50  dark:bg-[#333333]">
      {messages.map((message: Message, index: number) => (
        <div key={index}>
          {message.role === "coach" ? (
            (() => {
              const isLastCoachMessage = index === messages.length - 1;
              let componentToRender = null;

              if (isLastCoachMessage) {
                // For the last coach message, ONLY check the componentConfig prop (from cache)
                componentToRender = !isProcessingMessage && componentConfig ? componentConfig : null;
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
            <div className="mb-4 p-3.5 pr-4 pl-4 rounded-[18px] max-w-[85%] leading-[1.5] shadow-sm animate-fadeIn break-words mx-auto bg-red-500/70 text-center font-medium">
              {message.content}
            </div>
          )}
        </div>
      ))}
      {isProcessingMessage && (
        <CoachMessage>
          <LoadingBubbles />
        </CoachMessage>
      )}
      {/* Dummy div to scroll to bottom */}
      <div ref={messagesEndRef} />
    </div>
  );
};
