import React, { useRef, useEffect, useCallback } from "react";
import { ChatControls } from "@/pages/chat/components/ChatControls";
import { ChatMessages } from "@/pages/chat/components/ChatMessages";
import { useChatMessages } from "@/hooks/use-chat-messages";
import { useCoachState } from "@/hooks/use-coach-state";

/**
 * ChatInterface component
 * Handles the chat UI, message sending, and scrolling.
 * - Uses useChatMessages for chat history and sending messages.
 * - Optimistically updates the UI when sending messages.
 * - Always fetches fresh chat history on mount.
 * - Keeps 100% comment coverage for clarity.
 */
export const ChatInterface: React.FC = () => {
  // Reference to the end of the messages list for auto-scrolling
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Get chat messages and updateChatMessages mutation from the custom hook
  const {
    chatMessages,
    isLoading,
    isError,
    updateChatMessages,
    updateStatus,
    pendingMessage, // The message being sent (if any)
    isPending, // Whether a message is being sent
  } = useChatMessages();

  const { coachState } = useCoachState();

  // Compose the messages to display, including the pending message if any
  // This enables optimistic UI: the user's message appears immediately while sending
  const displayedMessages = React.useMemo(() => {
    if (isPending && pendingMessage?.content) {
      return [
        ...(chatMessages || []),
        {
          role: "user",
          content: pendingMessage.content,
          timestamp: new Date().toISOString(), // Temporary timestamp
        },
      ];
    }
    return chatMessages || [];
  }, [chatMessages, isPending, pendingMessage]);

  // Scroll to bottom when messages change
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages, scrollToBottom]);

  // Scroll to bottom when optimistic user message is added
  // This ensures the UI scrolls for both server and optimistic updates
  useEffect(() => {
    scrollToBottom();
  }, [displayedMessages, scrollToBottom]);

  // Handler for sending a message
  const handleSendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || updateStatus === "pending") return;
      // Call updateChatMessages with the new argument structure
      await updateChatMessages({ content });
    },
    [updateChatMessages, updateStatus]
  );

  // Handler for identity choice (if used)
  const handleIdentityChoice = useCallback(
    (response: string) => {
      handleSendMessage(response);
    },
    [handleSendMessage]
  );

  // If loading, show a loading state (optional)
  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        Loading chat...
      </div>
    );
  }
  if (isError) {
    return (
      <div className="flex-1 flex items-center justify-center text-red-500">
        Error loading chat messages.
      </div>
    );
  }

  return (
    <div className="_ChatInterface flex flex-col h-[100vh] rounded-md overflow-hidden shadow-gold-md bg-gold-50 transition-shadow hover:shadow-gold-lg dark:rounded-none">
      <ChatMessages
        messages={displayedMessages}
        isProcessingMessage={updateStatus === "pending"}
        handleIdentityChoice={handleIdentityChoice}
        messagesEndRef={messagesEndRef}
        coachState={coachState}
      />
      <ChatControls
        isProcessingMessage={updateStatus === "pending"}
        onSendMessage={handleSendMessage}
      />
    </div>
  );
};
