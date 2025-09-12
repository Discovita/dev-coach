import React from "react";
import { CoachMessage } from "@/pages/chat/components/CoachMessage";
import { CoachMessageWithComponent } from "@/pages/chat/components/CoachMessageWithComponent";
import { UserMessage } from "@/pages/chat/components/UserMessage";
import { IdentityChoice } from "@/pages/chat/components/IdentityChoice";
import MarkdownRenderer from "@/utils/MarkdownRenderer";
import { LoadingBubbles } from "@/pages/chat/components/LoadingBubbles";
import { Message } from "@/types/message";
import { CoachState } from "@/types/coachState";

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
  coachState?: CoachState;
  handleIdentityChoice: (response: string) => void;
  messagesEndRef: React.RefObject<HTMLDivElement | null>;
  /** Latest component config to render for the newest coach message (or null) */
  componentConfig?: import("@/types/componentConfig").ComponentConfig | null;
  /** Handler for component button selection (sends the label as a message) */
  onSelectComponentOption?: (label: string) => void;
}

export const ChatMessages: React.FC<ChatMessagesProps> = ({
  messages,
  isProcessingMessage,
  coachState,
  handleIdentityChoice,
  messagesEndRef,
  componentConfig,
  onSelectComponentOption,
}) => {
  return (
    <div className="_ChatMessages scrollbar not-last:flex-grow overflow-y-auto p-6 bg-gold-50  dark:bg-[#333333]">
      {messages.map((message: Message, index: number) => (
        <div key={index}>
          {message.role === "coach" ? (
            index === messages.length - 1 &&
            !!componentConfig &&
            !isProcessingMessage ? (
              <CoachMessageWithComponent
                componentConfig={componentConfig}
                onSelect={(label) =>
                  onSelectComponentOption && onSelectComponentOption(label)
                }
                disabled={isProcessingMessage}
              >
                <MarkdownRenderer content={message.content} />
              </CoachMessageWithComponent>
            ) : (
              <CoachMessage>
                <MarkdownRenderer content={message.content} />
                {index === messages.length - 1 &&
                  coachState?.proposed_identity &&
                  !isProcessingMessage && (
                    <IdentityChoice
                      identity={coachState.proposed_identity}
                      onChoiceSelected={handleIdentityChoice}
                      disabled={isProcessingMessage}
                    />
                  )}
              </CoachMessage>
            )
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
