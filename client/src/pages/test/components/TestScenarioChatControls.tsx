import React, { useCallback, useRef, useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ConversationExporter } from "@/pages/chat/components/ConversationExporter";
import { TestScenarioConversationResetter } from "@/pages/test/components/TestScenarioConversationResetter";
import { TestScenarioSessionFreezer } from "@/pages/test/components/TestScenarioSessionFreezer";
import { CoachRequest } from "@/types/coachRequest";



interface TestScenarioChatControlsProps {
  isProcessingMessage: boolean;
  onSendMessage: (request: CoachRequest) => void;
  scenarioId: string;
  testUserId: string; // Add testUserId prop
  onResetSuccess?: () => void;
}

export const TestScenarioChatControls: React.FC<
  TestScenarioChatControlsProps
> = ({ isProcessingMessage, onSendMessage, scenarioId, testUserId, onResetSuccess }) => {
  const [inputMessage, setInputMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);



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
    <div className="_TestScenarioChatControls bg-gold-200 dark:bg-[#333333] p-4">
      <form className="flex mb-3 relative items-center" onSubmit={handleSubmit}>
        <Textarea
          ref={textareaRef}
          value={inputMessage}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          disabled={isProcessingMessage}
          rows={1}
          className="flex-grow pr-4 pl-4 border border-primary-light rounded-[24px] text-[15px] font-inherit mr-3 transition-a resize-none overflow-y-hidden min-h-[46px] max-h-[500px] leading-[1.5] focus:shadow-[0_0_0_3px_rgba(208,169,89,0.2)] focus:bg-gold-50 disabled:bg-gold-50 disabled:cursor-not-allowed placeholder:text-neutral-400 placeholder:opacity-80"
        />
        <Button type="submit" disabled={isProcessingMessage}>
          {isProcessingMessage ? "Sending..." : "Send"}
        </Button>
      </form>
      <div className="flex justify-center items-center gap-6">
        <TestScenarioConversationResetter
          scenarioId={scenarioId}
          onResetSuccess={onResetSuccess}
        />
        <TestScenarioSessionFreezer
          userId={testUserId}
          onSuccess={() => {}}
        />
        <ConversationExporter />
      </div>
    </div>
  );
};
