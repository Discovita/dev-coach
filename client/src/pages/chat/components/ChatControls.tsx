import React, { useCallback, useRef, useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ConversationExporter } from '@/pages/test/components/ConversationExporter';
import { CoachState, Message } from '@/types/apiTypes';

interface ChatControlsProps {
  isLoading: boolean;
  onSendMessage: (msg: string) => void;
  messages: Message[];
  userId: string;
  coachState: CoachState;
}

export const ChatControls: React.FC<ChatControlsProps> = ({
  isLoading,
  onSendMessage,
  messages,
  userId,
  coachState,
}) => {
  const [inputMessage, setInputMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  /**
   * Resizes the textarea to fit content, up to a max height.
   * Called on input change and after sending a message.
   */
  const resizeTextarea = useCallback(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = 'auto';
    textarea.style.height = `${textarea.scrollHeight}px`;
    const maxHeight = 500;
    if (textarea.scrollHeight > maxHeight) {
      textarea.style.height = `${maxHeight}px`;
      textarea.classList.add('overflow');
    } else {
      textarea.classList.remove('overflow');
    }
  }, []);

  // Resize textarea on input change
  useEffect(() => {
    resizeTextarea();
  }, [inputMessage, resizeTextarea]);

  /**
   * Handles input change and resizes textarea.
   */
  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputMessage(e.target.value);
    // resizeTextarea will be called by useEffect
  }, []);

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      if (inputMessage.trim()) {
        onSendMessage(inputMessage);
        setInputMessage('');
        setTimeout(resizeTextarea, 0);
      }
    },
    [inputMessage, onSendMessage, resizeTextarea]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit(e);
      } else if (e.key === 'Enter' && e.shiftKey) {
        setTimeout(resizeTextarea, 0);
      }
    },
    [handleSubmit, resizeTextarea]
  );

  return (
    <div className="_ChatControls bg-gold-200 dark:bg-[#333333] p-4">
      <form className="flex mb-3 relative items-center" onSubmit={handleSubmit}>
        <Textarea
          ref={textareaRef}
          value={inputMessage}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          disabled={isLoading}
          rows={1}
          className="flex-grow pr-4 pl-4 border border-primary-light rounded-[24px] text-[15px] font-inherit mr-3 transition-a resize-none overflow-y-hidden min-h-[46px] max-h-[500px] leading-[1.5] focus:shadow-[0_0_0_3px_rgba(208,169,89,0.2)] focus:bg-gold-50 disabled:bg-gold-50 disabled:cursor-not-allowed placeholder:text-neutral-400 placeholder:opacity-80"
        />
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Sending...' : 'Send'}
        </Button>
      </form>
      <div className="flex justify-center items-center">
        <ConversationExporter messages={messages} userId={userId} coachState={coachState} />
      </div>
    </div>
  );
};
