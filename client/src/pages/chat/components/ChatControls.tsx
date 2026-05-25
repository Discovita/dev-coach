import React, { useCallback, useRef, useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import type { CoachRequest } from "@/types/coachRequest";
import { WarmupBulletin } from "@/pages/chat/components/WarmupBulletin";
import { BrainstormingBulletin } from "@/pages/chat/components/BrainstormingBulletin";
import { RefinementBulletin } from "@/pages/chat/components/RefinementBulletin";
import { CommitmentBulletin } from "@/pages/chat/components/CommitmentBulletin";
import { useIdentities } from "@/hooks/use-identities";
import { useCoachState } from "@/hooks/use-coach-state";
import { useComposerDisabled } from "@/hooks/use-composer-disabled";

interface ChatControlsProps {
  isProcessingMessage: boolean;
  onSendMessage: (request: CoachRequest) => void;
}

export const ChatControls: React.FC<ChatControlsProps> = ({
  isProcessingMessage,
  onSendMessage,
}) => {
  const [inputMessage, setInputMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Fetch coach state with active query subscription to ensure refetch on invalidation
  // This ensures bulletins update when coachState is invalidated after sending messages
  const { coachState } = useCoachState();
  const { identities } = useIdentities();

  // Coaching Phase Videos (PR 15 + PR 18): composer disables on
  // `on_break === true` OR when the latest coach message is an
  // unacknowledged SESSION_VIDEO. Centralized in `useComposerDisabled`.
  const composerDisabled = useComposerDisabled(isProcessingMessage);

  /**
   * Resizes the textarea to fit content, up to a max height.
   * Called on input change and after sending a message.
   */
  const resizeTextarea = useCallback(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = "auto";
    textarea.style.height = `${textarea.scrollHeight}px`;
    const maxHeight = 500;
    if (textarea.scrollHeight > maxHeight) {
      textarea.style.height = `${maxHeight}px`;
      textarea.classList.add("overflow");
    } else {
      textarea.classList.remove("overflow");
    }
  }, []);

  // Resize textarea on input change
  useEffect(() => {
    resizeTextarea();
  }, [inputMessage, resizeTextarea]);

  // Auto-focus textarea when coach finishes responding
  // This allows users to immediately type their next message without clicking
  const prevIsProcessingRef = useRef(isProcessingMessage);
  useEffect(() => {
    // Only focus when transitioning from processing (true) to not processing (false)
    // This avoids focusing on initial mount or when already not processing
    if (prevIsProcessingRef.current === true && !isProcessingMessage && textareaRef.current) {
      setTimeout(() => {
        textareaRef.current?.focus();
      }, 0);
    }
    prevIsProcessingRef.current = isProcessingMessage;
  }, [isProcessingMessage]);

  /**
   * Handles input change and resizes textarea.
   */
  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      setInputMessage(e.target.value);
      // resizeTextarea will be called by useEffect
    },
    []
  );

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      if (inputMessage.trim()) {
        onSendMessage({ message: inputMessage });
        setInputMessage("");
        setTimeout(resizeTextarea, 0);
      }
    },
    [inputMessage, onSendMessage, resizeTextarea]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSubmit(e);
      } else if (e.key === "Enter" && e.shiftKey) {
        setTimeout(resizeTextarea, 0);
      }
    },
    [handleSubmit, resizeTextarea]
  );

  return (
    <div className="_ChatControls bg-gold-200 dark:bg-[#333333] sm:p-4">
      <WarmupBulletin coachState={coachState} />
      <BrainstormingBulletin coachState={coachState} identities={identities} />
      <RefinementBulletin coachState={coachState} />
      <CommitmentBulletin coachState={coachState} />
      <form className="flex mb-3 relative items-center" onSubmit={handleSubmit}>
        <Textarea
          ref={textareaRef}
          value={inputMessage}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          disabled={composerDisabled}
          rows={1}
          className="flex-grow pr-4 pl-4 border border-primary-light rounded-[24px] text-[15px] font-inherit mr-3 transition-a resize-none overflow-y-hidden min-h-[46px] max-h-[500px] leading-[1.5] focus:shadow-[0_0_0_3px_rgba(208,169,89,0.2)] focus:bg-gold-50 disabled:bg-gold-50 disabled:cursor-not-allowed placeholder:text-neutral-400 placeholder:opacity-80"
        />
        <Button type="submit" disabled={composerDisabled}>
          {isProcessingMessage ? "Sending..." : "Send"}
        </Button>
      </form>
    </div>
  );
};
